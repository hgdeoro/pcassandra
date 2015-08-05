import logging

from django import VERSION
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
    """Like Django's AbstractBaseUser"""
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
    """Like Django's AbstractUser"""
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
    """Like Django's PermissionsMixin"""
    __abstract__ = True

    is_superuser = cassandra_columns.Boolean(default=False)
    groups = cassandra_columns.Set(cassandra_columns.Text)
    user_permissions = cassandra_columns.Set(cassandra_columns.Text)

    def get_group_permissions(self, obj=None):
        # pC* FIXME: implement get_group_permissions()
        return set()

    def get_all_permissions(self, obj=None):
        # pC* FIXME: implement get_all_permissions()
        return set()

    def has_perm(self, perm, obj=None):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # pC* FIXME: implement has_perm()
        return False

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # pC* FIXME: implement has_module_perms()
        return False


class CassandraAbstractUser(EmulatedAbstractUser, CassandraPermissionsMixin):
    """
    If you need a custom model for your user, just use
    CassandraAbstractUser as the superclass.
    """
    _if_not_exists = True  # required by cqlengine to ensure 'unique' usernames
    __abstract__ = True


class CassandraUser(CassandraAbstractUser):
    pass
