from django.core.management.base import BaseCommand

from pcassandra import connection


class Command(BaseCommand):
    help = 'Test Cassandra connection and access to keyspace'

    def handle(self, *args, **options):
        connection.setup_connection_if_unset(set_default_keyspace=False)
        connection.test_connection(verbose=True)
        connection.test_keyspace(verbose=True)
