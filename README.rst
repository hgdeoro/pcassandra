PCassandra - Pico Cassandra utilities for Django
================================================


How to execute unittests
------------------------

    env TEST_KEYSPACE_SUFFIX=_$(date +%s) \
        bash -c 'python manage.py pcassandra_create_keyspace ; python manage.py test pcassandra'
