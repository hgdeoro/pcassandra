from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from pcassandra.dj18.models import CassandraAbstractUser


def get_cassandra_user_model():
    """
    Returns the User model that is active in this project.
    """
    # Code taken from `django.contrib.auth.get_user_model()`
    try:
        class_name = settings.PCASSANDRA_AUTH_USER_MODEL
    except AttributeError:
        raise ImproperlyConfigured("PCASSANDRA_AUTH_USER_MODEL must be configured in settings")

    try:
        clazz = import_string(class_name)
    except ImportError:
        raise ImproperlyConfigured("Class referenced by PCASSANDRA_AUTH_USER_MODEL "
                                   "couldn't be loaded: '{}'".format(class_name))

    if not issubclass(clazz, CassandraAbstractUser):
        raise ImproperlyConfigured("Class referenced by PCASSANDRA_AUTH_USER_MODEL "
                                   "is not a subclass of CassandraAbstractUser")

    return clazz
