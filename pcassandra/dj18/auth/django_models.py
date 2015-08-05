"""
Implements a Django model, with the API of the standard User,
but contains just the 'username' field. This instance is
persisted in the traditional database configured in your project.

It acts as a proxy to the real user, stored in Cassadra.

It's required because the way Django is designed, and it's
the recommended way to handle this situation:

    <<
    The Django admin system is tightly coupled to the Django User
    object described at the beginning of this document. For now,
    the best way to deal with this is to create a Django User object
    for each user that exists for your backend (e.g., in your LDAP
    directory, your external SQL database, etc.) You can either write
    a script to do this in advance, or your authenticate method can
    do it the first time a user logs in.
    >>

    See https://docs.djangoproject.com/en/1.8/topics/auth/customizing/

The first time the user is authenticated, the 'DjangoUserProxy' instance
is created if not exists.

"""
import logging

from django import VERSION
from django.db import models
from django.utils.crypto import salted_hmac

from pcassandra.dj18.auth.models import CassandraAbstractUser

logger = logging.getLogger(__name__)


assert VERSION[0] == 1 and VERSION[1] == 8, "Django 1.8 required"


class DjangoUserProxy(models.Model):

    def __init__(self, *args, **kwargs):
        super(DjangoUserProxy, self).__init__(*args, **kwargs)
        self._cassandra_user = None

    @property
    def cassandra_user(self):
        return self._cassandra_user

    @cassandra_user.setter
    def cassandra_user(self, cassandra_user):
        assert isinstance(cassandra_user, CassandraAbstractUser)
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
        return self._cassandra_user.email_user(subject, message, from_email, **kwargs)

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
        """
        The Django's authenticate() updates the 'last_login' field as part
        of the login process. There is no way to avoid this, so, we check the
        arguments. If the arguments are the exact arguments used by authenticate(),
        we ignore the call to save().

        This is an ugly hack, please, tell me if you know a better way to handle this.
        """
        update_fields = kwargs.get('update_fields', None)
        if (update_fields == ['last_login'] and
                len(kwargs) == 1 and
                len(args) == 0):
            logger.info("Ignoring save() because is just trying to update 'last_login'")
        else:
            return super().save(*args, **kwargs)
