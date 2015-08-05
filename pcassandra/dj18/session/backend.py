import logging

from django.contrib.sessions.backends.base import CreateError
from django.contrib.sessions.backends.base import SessionBase as DjangoSessionBase
from django.core.exceptions import SuspiciousOperation
from django.utils import timezone
from django.utils.encoding import force_text

from cassandra.cqlengine.query import LWTException


class SessionExpiredHack(Exception):
    """
    Internal exception to indicate the session is expired.
    Required because in Cassandra we don't filter by expiration date
    """
    pass


class CassandraSessionStore(DjangoSessionBase):

    def __init__(self, session_key=None):
        super(CassandraSessionStore, self).__init__(session_key)

    def load(self):
        try:
            s = models.CassandraSession.get(
                session_key=self.session_key,
                # expire_date__gt=timezone.now()
            )
            # ------------------------------------------------------------
            # pcassandra: note on `expire_date__gt`
            # ------------------------------------------------------------
            # We can't use 'expire_date__gt', so we use manually raise
            # SessionExpiredHack, since `DoesNotExist` won't be raised
            # when the session is expired
            # ------------------------------------------------------------

            tz_aware_expire_date = timezone.make_aware(s.expire_date)
            if tz_aware_expire_date < timezone.now():
                raise SessionExpiredHack()
            return self.decode(s.session_data)
        except (models.CassandraSession.DoesNotExist,
                SuspiciousOperation,
                SessionExpiredHack) as e:
            if isinstance(e, SuspiciousOperation):
                logger = logging.getLogger('django.security.%s' %
                        e.__class__.__name__)
                logger.warning(force_text(e))
            self._session_key = None
            return {}

    def exists(self, session_key):
        # ------------------------------------------------------------
        # pcassandra: note on `exists()`
        # ------------------------------------------------------------
        # We can't use 'exists()', so, we just try to get the
        # object. Since the session_key es the ROW-ID, it's a
        # cheap operation.
        # We could improve this selecting just the session_key, to
        # avoid the materializtion of the object...
        # ------------------------------------------------------------
        try:
            models.CassandraSession.get(session_key=session_key)
            return True
        except models.CassandraSession.DoesNotExist:
            return False

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database. If 'must_create' is
        True, a database error will be raised if the saving operation doesn't
        create a *new* entry (as opposed to possibly updating an existing
        entry).
        """
        if self.session_key is None:
            return self.create()

        obj = models.CassandraSession(
            session_key=self._get_or_create_session_key(),
            session_data=self.encode(self._get_session(no_load=must_create)),
            expire_date=self.get_expiry_date(),
        )

        try:
            # obj.save(force_insert=must_create)
            if must_create:
                # FORCE INSERT
                obj.if_not_exists(True).save()
            else:
                # Don't mind if insert or update
                obj.save()

        # ------------------------------------------------------------
        # pcassandra: note on IntegrityError
        # ------------------------------------------------------------
        # see: https://docs.djangoproject.com/en/1.8/ref/exceptions/#database-exceptions
        # see: https://code.djangoproject.com/wiki/IntegrityError
        # see: https://www.python.org/dev/peps/pep-0249/
        #  * Exception raised when the relational integrity of the
        #    database is affected, e.g. a foreign key check fails
        #    duplicated keys
        #
        # Seems like it's used to detect duplicated keys. Assuming
        #  that, we check for 'LWTException', that is raised when
        #  the insert fails because of the key already exists
        # ------------------------------------------------------------

        # except IntegrityError:
        #     if must_create:
        #         raise CreateError
        #     raise
        except LWTException:
            if must_create:
                raise CreateError
            raise

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key

        try:
            models.CassandraSession.get(session_key=session_key).delete()
        except models.CassandraSession.DoesNotExist:
            pass

    @classmethod
    def clear_expired(cls):
        # FIXME: pcassandra: implement 'clear_expired()'
        # models.CassandraSession.objects.filter(expire_date__lt=timezone.now()).delete()
        pass


SessionStore = CassandraSessionStore


# At bottom to avoid circular import
# from django.contrib.sessions.models import Session  # isort:skip
from pcassandra.dj18.session import models
