#!/bin/bash


cd $(dirname $0)

env TEST_KEYSPACE_SUFFIX="_$(date +%s)" PYTHONPATH=. python pcassandra/dj18/tests/manage.py test
