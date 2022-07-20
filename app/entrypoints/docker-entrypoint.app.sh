#!/bin/env bash

bash entrypoints/wait-for-it.sh "${DB_HOST}":3306 --timeout=0 &&
bash entrypoints/wait-for-it.sh nginx:80 --timeout=0 &&
python manage.py makemigrations &&
python manage.py migrate &&
python manage.py createsuperuser --noinput &&
bash entrypoints/load_initial_data.sh &&
#./manage.py shell < entrypoints/setup_initial_periodic_tasks.py &&
bash entrypoints/load_example_data.sh &&
gunicorn app.wsgi:application --bind 0.0.0.0:8000
