import logging

from django import VERSION
from django.db import models
from django.contrib.auth.hashers import (
    is_password_usable, make_password, check_password
)
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import salted_hmac

from cassandra.cqlengine import columns as cassandra_columns
from cassandra.cqlengine import models as cassandra_models

logger = logging.getLogger(__name__)


assert VERSION[0] == 1 and VERSION[1] == 8, "Django 1.8 required"


# ----------------------------------------------------------------------
# Cassandra model for user
# ----------------------------------------------------------------------

class EmulatedAbstractBaseUser(cassandra_models.Model):
    __abstract__ = True

    password = cassandra_columns.Text()
    last_login = cassandra_columns.DateTime()

    def get_username(self):
        """Return the identifying username for this User"""
        return getattr(self, self.USERNAME_FIELD)

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        # pC* FIXME: Django's implementtion update password hash
        # def setter(raw_password):
        #     # self.set_password(raw_password)
        #     # self.save(update_fields=["password"])
        #     raise NotImplemented()
        # return check_password(raw_password, self.password, setter)
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        return is_password_usable(self.password)

    def get_session_auth_hash(self):
        """
        Returns an HMAC of the password field.
        """
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()


class EmulatedAbstractUser(EmulatedAbstractBaseUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    __abstract__ = True

    username = cassandra_columns.Text(
        min_length=4,
        max_length=30,
        primary_key=True,
    )
    # pC* FIXME: validate characters used in username
    # pC* FIXME: validate uniqueness
    # validators=[
    #     validators.RegexValidator(r'^[\w.@+-]+$',
    #                               _('Enter a valid username. '
    #                                 'This value may contain only letters, numbers '
    #                                 'and @/./+/-/_ characters.'), 'invalid'),
    # ],

    first_name = cassandra_columns.Text(max_length=100)
    last_name = cassandra_columns.Text(max_length=100)
    # pC* FIXME: validate email
    email = cassandra_columns.Text()
    is_staff = cassandra_columns.Boolean(default=False)
    is_active = cassandra_columns.Boolean(default=True)
    # pC* FIXME: it's ok to use 'timezone.now'?
    date_joined = cassandra_columns.DateTime(default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class CassandraPermissionsMixin(EmulatedAbstractBaseUser):
    """
    A mixin class that adds the fields and methods necessary to support
    Django's Group and Permission model using the ModelBackend.
    """
    __abstract__ = True

    is_superuser = cassandra_columns.Boolean(default=False)
    groups = cassandra_columns.Set(cassandra_columns.Text)
    user_permissions = cassandra_columns.Set(cassandra_columns.Text)

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        # pC* FIXME: implement get_group_permissions()
        return set()

    def get_all_permissions(self, obj=None):
        # pC* FIXME: implement get_all_permissions()
        return set()

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # pC* FIXME: implement get_group_permissions()
        return False

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # pC* FIXME: implement get_group_permissions()
        return False


class CassandraAbstractUser(EmulatedAbstractUser, CassandraPermissionsMixin):
    _if_not_exists = True  # required by cqlengine to ensure 'unique' usernames
    __abstract__ = True


class CassandraUser(CassandraAbstractUser):
    pass


# ----------------------------------------------------------------------
# Django model
# ----------------------------------------------------------------------

class DjangoUserProxy(models.Model):

    def __init__(self, *args, **kwargs):
        super(DjangoUserProxy, self).__init__(*args, **kwargs)
        self._cassandra_user = None

    @property
    def cassandra_user(self):
        return self._cassandra_user

    @cassandra_user.setter
    def cassandra_user(self, cassandra_user):
        assert isinstance(cassandra_user, CassandraUser)
        assert cassandra_user.username is not None
        assert self.username == cassandra_user.username
        assert self._cassandra_user is None
        self._cassandra_user = cassandra_user

    # ----- AbstractBaseUser || Fake attributes

    # password = models.CharField(_('password'), max_length=128)
    # last_login = models.DateTimeField(_('last login'), blank=True, null=True)

    @property
    def password(self):
        return self._cassandra_user.password

    @property
    def last_login(self):
        return self._cassandra_user.last_login

    @last_login.setter
    def last_login(self, new_value):
        # FIXME: implement this
        logging.warning("DjangoUserProxy: ignoring new value for 'last_login'")

    # ----- AbstractBaseUser || Fake methods

    def get_username(self):
        """Return the identifying username for this User"""
        return getattr(self, self.USERNAME_FIELD)

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        return self._cassandra_user.set_password(raw_password)

    def check_password(self, raw_password):
        return self._cassandra_user.check_password(raw_password)

    def set_unusable_password(self):
        return self._cassandra_user.set_unusable_password()

    def has_usable_password(self):
        return self._cassandra_user.has_usable_password()

    def get_session_auth_hash(self):
        return self._cassandra_user.get_session_auth_hash()

    def get_full_name(self):
        return self._cassandra_user.get_full_name()

    def get_short_name(self):
        return self._cassandra_user.get_short_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        return self._cassandra_user.email_user(subject, message, from_email=None, **kwargs)

    def __str__(self):
        return self.get_username()

    def get_session_auth_hash(self):
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self._cassandra_user.password).hexdigest()

    # ----- PermissionsMixin || Fake attributes

    @property
    def is_superuser(self):
        return self._cassandra_user.is_superuser

    @property
    def groups(self):
        # FIXME: implement this
        return ()

    @property
    def user_permissions(self):
        # FIXME: implement this
        return ()

    # ----- PermissionsMixin || Fake methods

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        if self._cassandra_user.is_active and self._cassandra_user.is_superuser:
            return True
        return False

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        if self._cassandra_user.is_active and self._cassandra_user.is_superuser:
            return True
        return False

    # ----- AbstractUser || Fake attributes

    username = models.CharField(max_length=30, primary_key=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ()

    # first_name = models.CharField(_('first name'), max_length=30, blank=True)
    # last_name = models.CharField(_('last name'), max_length=30, blank=True)
    # email = models.EmailField(_('email address'), blank=True)
    # is_staff = models.BooleanField(_('staff status'), default=False,
    # is_active = models.BooleanField(_('active'), default=True,
    # date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    @property
    def first_name(self):
        return self._cassandra_user.first_name

    @property
    def last_name(self):
        return self._cassandra_user.last_name

    @property
    def email(self):
        return self._cassandra_user.email

    @property
    def is_staff(self):
        return self._cassandra_user.is_staff

    @property
    def is_active(self):
        return self._cassandra_user.is_active

    @property
    def date_joined(self):
        return self._cassandra_user.date_joined

    # ----- AbstractUser || Fake methods

    # None!

    # ----- Other hacks

    def save(self, *args, **kwargs):
        """The Django's authenticate() updates the 'last_login' field as part
        of the login process. There is no way to avoid this, so, we check the
        arguments. If the arguments are the exact arguments used by authenticate(),
        we ignore the call to save().

        This is an ugly hack, please, tell me if you know a better way to handle this.
        """
        update_fields = kwargs.get('update_fields', None)
        if (update_fields == ['last_login'] and
                len(kwargs) == 1 and
                len(args) == 0):
            logger.warning("Ignoring save() because is just trying to update 'last_login'")
        else:
            return super().save(*args, **kwargs)
