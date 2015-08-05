"""
WSGI config for dj18tests project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from pcassandra.dj18 import wsgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj18test_app.settings")

application = get_wsgi_application()
application_development = wsgi.CassandraConnectionSetupWsgiMiddleware(get_wsgi_application())
