#!/bin/bash

# DB
if [ "$PRODUCTION" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

./manage.py collectstatic --noinput;

./manage.py makemigrations;
./manage.py migrate;

gunicorn --workers=9 --bind 0.0.0.0:8000 thebackend.wsgi:application --log-level DEBUG;" 

exec "$@"
