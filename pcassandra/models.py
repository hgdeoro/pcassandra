from django import VERSION

from pcassandra.dj18.auth.models import DjangoUserProxy

#
# We need the models be accesibles from this module because the
# way the 'AUTH_USER_MODEL' settings works
#

assert VERSION[0] == 1 and VERSION[1] == 8, "Django 1.8 required"

__all__ = ["DjangoUserProxy"]
