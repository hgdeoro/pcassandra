import logging

from django import VERSION
from cassandra.cqlengine import columns as cassandra_columns
from cassandra.cqlengine import models as cassandra_models

logger = logging.getLogger(__name__)

assert VERSION[0] == 1 and VERSION[1] == 8, "Django 1.8 required"


class CassandraSessionManager:

    # def encode(self, session_dict):
    #     """
    #     Returns the given session dictionary serialized and encoded as a string.
    #     """
    #     return DjangoSessionStore().encode(session_dict)

    def save(self, session_key, session_dict, expire_date):
        s = CassandraSession(session_key=session_key,
                             session_data=DjangoSessionStore().encode(session_dict),
                             expire_date=expire_date)

        if session_dict:
            s.save()
        else:
            # FIXME: pcassandra: does delete works this way with Cassandra/cqlengine?
            # FIXME: pcassandra: what would happen if 'session_key' is None?
            #   Make sure that don't delete all the table
            s.delete()  # Clear sessions with no data.
        return s


class CassandraSession(cassandra_models.Model):
    session_key = cassandra_columns.Text(primary_key=True, max_length=40)
    expire_date = cassandra_columns.DateTime()
    session_data = cassandra_columns.Text()

    mngr = CassandraSessionManager()

    def __str__(self):
        return self.session_key

    # def get_decoded(self):
    #     return DjangoSessionStore().decode(self.session_data)


# At bottom to avoid circular import
from django.contrib.sessions.backends.db import SessionStore as DjangoSessionStore  # isort:skip
