import logging

from django import VERSION

from pcassandra.dj18.auth.models import DjangoUserProxy
from pcassandra import utils

assert VERSION[0] == 1 and VERSION[1] == 8, "Django 1.8 required"


logger = logging.getLogger(__name__)


class ModelBackend:
    """Auth backend, lookup user instances in Cassandra"""

    _CASSANDRA_USER_MODEL = None

    @classmethod
    def _get_cassandra_user_model(cls):
        if not cls._CASSANDRA_USER_MODEL:
            cls._CASSANDRA_USER_MODEL = utils.get_cassandra_user_model()
        return cls._CASSANDRA_USER_MODEL

    def _get_django_user_proxy(self, cassandra_user):
        """Returns the instance of DjangoUserProxy, with the required reference
        to CassandraUser. If the instance of DjangoUserProxy does not exists,
        the instance is created.

        This is implemented this way following the Django's doc sugestion:

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
        """
        assert isinstance(cassandra_user, self._get_cassandra_user_model())
        try:
            dj_user = DjangoUserProxy.objects.get(username=cassandra_user.username)
        except DjangoUserProxy.DoesNotExist:
            dj_user = DjangoUserProxy.objects.create(username=cassandra_user.username)
            logger.info("Django user for '%s' was created", cassandra_user.username)
        dj_user.cassandra_user = cassandra_user
        return dj_user

    def authenticate(self, username=None, password=None, **kwargs):
        assert username is not None, "No username provided"
        MODEL = self._get_cassandra_user_model()
        try:
            cassandra_user = MODEL.get(username=username)
            if cassandra_user.check_password(password):
                return self._get_django_user_proxy(cassandra_user)
        except MODEL.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            MODEL().set_password(password)

    def get_user(self, user_id):
        MODEL = self._get_cassandra_user_model()
        try:
            cassandra_user = MODEL.get(username=user_id)
            return self._get_django_user_proxy(cassandra_user)
        except MODEL.DoesNotExist:
            return None
