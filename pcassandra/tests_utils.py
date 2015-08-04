"""
Utilities to facilitate the implementation of unittest, for
pcassandra, and for pcassandra users too.
"""

import uuid

from cassandra.cqlengine import management

from pcassandra import connection
from pcassandra import utils


class PCassandraTestUtilsMixin:

    def _full_setup(self_or_cls=None):
        """
        Setup connection, create keyspace and models.

        Use: call this in the 'setUpClass()' method of the base class of your unittests:

            class BaseTest(unittest.TestCase, tests_utils.PCassandraTestUtilsMixin):

                cassandra_connection_done = False

                @classmethod
                def setUpClass(cls):
                    unittest.TestCase.setUpClass()
                    if not cls.cassandra_connection_done:
                        tests_utils.PCassandraTestUtilsMixin._full_setup()
                        cls.cassandra_connection_done = True
        """
        # FIXME: self_or_cls=None... So hacky!
        ModelClass = utils.get_cassandra_user_model()

        connection.setup_connection_if_unset(set_default_keyspace=False)
        connection.create_keyspace()
        connection.set_session_default_keyspace()
        management.sync_table(ModelClass)

    def _create_user(self, username=None, auto_first_last_email=False, **kwargs):
        """
        Creates an user instance and inserts it in the database.
        The received 'kwargs' are passed to YourConfiguredUserModel.create()
        """
        ModelClass = utils.get_cassandra_user_model()

        if username is None:
            rnd = uuid.uuid4().hex[0:20]
            username = "user-{}".format(rnd)

        if auto_first_last_email:
            kwargs['first_name'] = kwargs.get('first_name', "John '{}'".format(username))
            kwargs['last_name'] = kwargs.get('last_name', "Doe")
            kwargs['email'] = kwargs.get('email', "{}@example.com".format(username))

        cassandra_user = ModelClass.create(username=username, **kwargs)
        return cassandra_user
