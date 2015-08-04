from pcassandra import connection


class CassandraConnectionSetupWsgiMiddleware:
    """WSGI middleware, setup the Cassandra connection when receiving the first request

    To use it, create a 'development version' of the 'WSGI application':

    * Add to `wsgi.py`:

        from pcassandra.dj18 import wsgi
        application_development = wsgi.CassandraConnectionSetupWsgiMiddleware(get_wsgi_application())

    * Add to `settings_development.py`:

        WSGI_APPLICATION = 'MYAPP.wsgi.application_development'

    """

    def __init__(self, app):
        self.application = app
        self.setup_done = False

    def __call__(self, environ, start_response):
        if not self.setup_done:
            connection.setup_connection_if_unset()
        return self.application(environ, start_response)
