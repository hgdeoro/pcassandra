from django.core.management.base import BaseCommand
from cassandra.cqlengine import management

from pcassandra import connection
from pcassandra import utils


class Command(BaseCommand):
    help = 'Sync Cassandra tables'

    def handle(self, *args, **options):
        connection.setup_connection_if_unset()
        connection.create_keyspace()
        ConfiguredCassandraUserModelClass = utils.get_cassandra_user_model()
        self.stdout.write('Sync-ing "{}"'.format(ConfiguredCassandraUserModelClass))
        management.sync_table(ConfiguredCassandraUserModelClass)
