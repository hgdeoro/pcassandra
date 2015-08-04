"""
Setup the connections to Cassandra using the values on Django settings
"""

import logging

from cassandra.cqlengine import connection
from django.conf import settings

logger = logging.getLogger(__name__)


def setup_connection(set_default_keyspace=True):
    """Set 'cqlengine' connection settings"""
    if connection.session is not None:
        logger.warn("setup_connection(): connection already configured. "
                    "Will overwrite old settings")
    connection.setup(settings.CASSANDRA_CONNECTION['HOSTS'],
                     default_keyspace=settings.CASSANDRA_CONNECTION['KEYSPACE'],
                     **settings.CASSANDRA_CONNECTION['CLUSTER_KWARGS'])
    if set_default_keyspace:
        # Management commands that creates keyspaces requires a way to
        #  create connections when the keyspaces doesn't exists yet
        set_session_default_keyspace()

    logger.info("setup_connection(): cassandra.cqlengine.connection.setup() done")


def create_keyspace():
    logger.info("create_keyspace(): creating keyspace %s",
                settings.CASSANDRA_CONNECTION['KEYSPACE'])
    connection.execute("CREATE KEYSPACE IF NOT EXISTS {} WITH REPLICATION = {}".format(
        settings.CASSANDRA_CONNECTION['KEYSPACE'],
        settings.CASSANDRA_CONNECTION['KEYSPACE_REPLICATION']
    ))


def set_session_default_keyspace():
    connection.session.set_keyspace(settings.CASSANDRA_CONNECTION['KEYSPACE'])


def setup_connection_if_unset(**kwargs):
    if connection.session is None:
        logger.info("setup_connection_if_unset(): connection wasn't setted up. "
                    "Wil call setup_connection()")
        setup_connection(**kwargs)


def test_connection(verbose=False):
    response = connection.execute("SELECT now() AS response FROM system.schema_columns LIMIT 1;")
    if verbose:
        print("--- Connection to Cassandra OK: {}".format(response[0]['response']))


def test_keyspace(verbose=False):
    connection.execute("USE {};".format(settings.CASSANDRA_CONNECTION['KEYSPACE']))
    if verbose:
        print("--- Keyspace OK")
