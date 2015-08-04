import uuid

from django import test
from django.contrib import auth
from django.test.utils import override_settings

from pcassandra import tests_utils
from pcassandra.dj18 import models


class PCassandraBaseTest(test.TestCase, tests_utils.PCassandraTestUtilsMixin):
    @classmethod
    @override_settings(PCASSANDRA_AUTH_USER_MODEL='pcassandra.dj18.models.CassandraUser')
    def setUpClass(cls):
        test.TestCase.setUpClass()
        cls._full_setup()


class TestCassandraUserCreation(PCassandraBaseTest):
    @override_settings(PCASSANDRA_AUTH_USER_MODEL='pcassandra.dj18.models.CassandraUser')
    def test_create_valid_user(self):
        rnd = uuid.uuid4().hex[0:20]
        username = "user-{}".format(rnd)

        all_users = models.CassandraUser.all()
        all_usernames = [_.username for _ in all_users]
        self.assertNotIn(username, all_usernames)

        cassandra_user = self._create_user(username)

        all_users = models.CassandraUser.all()
        all_usernames = [_.username for _ in all_users]
        self.assertIn(username, all_usernames)


class TestAuthentication(PCassandraBaseTest):
    @override_settings(PCASSANDRA_AUTH_USER_MODEL='pcassandra.dj18.models.CassandraUser')
    def test_authenticate_works(self):
        password = 'pass-{}'.format(uuid.uuid4().hex)
        cassandra_user = self._create_user()

        self.assertIsNone(auth.authenticate(
            username=cassandra_user.username,
            password=password))

        cassandra_user.set_password(password)
        cassandra_user.save()

        auth_user = auth.authenticate(
            username=cassandra_user.username,
            password=password)

        self.assertIsNotNone(auth_user)
        self.assertEquals(auth_user.username,
                          cassandra_user.username)
