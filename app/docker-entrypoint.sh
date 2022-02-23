#!/bin/env bash

python manage.py makemigrations &&
python manage.py migrate &&
python manage.py loaddata setup_survey_data.yaml &&
python manage.py loaddata setup_filter_data.yaml &&
python manage.py loaddata setup_catalog_data.yaml &&
python manage.py loaddata setup_test_transient.yaml &&
python manage.py loaddata setup_tasks.yaml &&
python manage.py loaddata setup_status.yaml &&
gunicorn app.wsgi:application --bind 0.0.0.0:8000
#python manage.py runserver 0.0.0.0:8000