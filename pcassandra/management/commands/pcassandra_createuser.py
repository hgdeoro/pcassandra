import getpass
import sys

from django.core.management.base import BaseCommand
from django.utils.six.moves import input

from pcassandra import connection
from pcassandra import utils


class Command(BaseCommand):
    help = 'Create a CassandraUser'
    SUPERUSER = False

    def handle(self, *args, **options):
        connection.setup_connection_if_unset()

        ConfiguredCassandraUserModelClass = utils.get_cassandra_user_model()
        username = input("Enter the username: ")
        user = ConfiguredCassandraUserModelClass()

        password = getpass.getpass("Password: ")
        password2 = getpass.getpass("Password (again): ")

        if password != password2:
            print("ERROR: password mismatch")
            sys.exit(1)

        user.username = username.strip()
        user.email = '{}@example.com'.format(username)
        user.set_password(username)
        user.is_staff = self.SUPERUSER
        user.is_superuser = self.SUPERUSER
        user.save()
        print("User '{}' created".format(username))
