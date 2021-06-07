#!/bin/sh

set -e

python manage.py sync_cassandra

uwsgi --socket :8000 --master --enable-threads --module app.wsgi