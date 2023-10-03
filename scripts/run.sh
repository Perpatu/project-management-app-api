#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser

uwsgi --socket :9000 --workers 12 --master --enable-threads --module app.wsgi