#! /bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 --workers 2 config.wsgi:application --reload

# python manage.py runserver
