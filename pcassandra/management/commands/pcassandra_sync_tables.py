from django.core.management.base import BaseCommand
from cassandra.cqlengine import management

from pcassandra import connection
from pcassandra import utils
from pcassandra.dj18.session import models as session_models


class Command(BaseCommand):
    help = 'Sync Cassandra tables'

    def handle(self, *args, **options):
        connection.setup_connection_if_unset()
        connection.create_keyspace()
        ConfiguredCassandraUserModelClass = utils.get_cassandra_user_model()
        self.stdout.write('Sync-ing "{}"'.format(ConfiguredCassandraUserModelClass))
        management.sync_table(ConfiguredCassandraUserModelClass)

        self.stdout.write('Sync-ing "{}"'.format(session_models.CassandraSession))
        management.sync_table(session_models.CassandraSession)
