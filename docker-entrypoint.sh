#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput


gunicorn -w $(nproc) --bind 0.0.0.0:8000 apps.wsgi
