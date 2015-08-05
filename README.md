# PCassandra - Pico Cassandra utilities for Django

... because nano is too much, but femto is not enough :-P

- store User on Cassadra (custom auth backend) - see KNOWN ISSUES
- store Session on Cassandra (custom session store) - see KNOWN ISSUES
- configure cqlengine connection parameters from your settings
- management commands to create keyspace and sync models (auth, session)
- management commands to create user and superusers
- a WSGI middleware to setup cqlengine on development server

Since Django's auth & session backends are by design heavyly coupled with models,
the backends included here are basically and copy & paste of Django, adapted for
the API of cqlengine models.

### Developed and tested with

* Python 3.4
* Django 1.8.3
* cassandra-driver 2.6.0
* Cassandra 2.1.8

## Install

    $ pip install pcassandra

## Settings

PCassandra adds 2 new settings variables:

* `CASSANDRA_CONNECTION`: see *connection.py*
* `PCASSANDRA_AUTH_USER_MODEL = 'pcassandra.dj18.auth.models.CassandraUser'`

And you'll need to override some defaults values with:

* `AUTHENTICATION_BACKENDS = `['pcassandra.dj18.auth.backend.ModelBackend']`
* `AUTH_USER_MODEL = 'pcassandra.DjangoUserProxy'`
* `SESSION_ENGINE = 'pcassandra.dj18.session.backend'`
* `WSGI_APPLICATION`: see *wsgi.py* for recommended setup

## TODO

- Auth: add unittest of user model / auth backend
- Auth: implement user's permissions
- Auth: create management command to change user passwords
- Session: add unittest of session model / backend
- Session: implement 'clear_expired()'
- Both: document the ugliest parts, and create unittests for them
- generate docs
- investigate if there is some way to execute Django's unittests against this implementations

## KNOWN ISSUES

- User model DOES NOT implements permissions api. Superusers have all the permissions,
  and non-superusers have no permissions.
- Session model and session backend is not tested at all


# LICENSE

Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
