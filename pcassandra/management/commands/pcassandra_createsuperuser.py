from pcassandra.management.commands import pcassandra_createuser


class Command(pcassandra_createuser.Command):
    help = 'Create a CassandraUser superuser'
    SUPERUSER = True
