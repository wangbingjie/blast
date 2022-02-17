#!/bin/env bash

python manage.py makemigrations &&
python manage.py migrate &&
python manage.py loaddata setup_survey_data.yaml &&
python manage.py loaddata setup_filter_data.yaml &&
python manage.py loaddata setup_catalog_data.yaml &&
python manage.py loaddata setup_test_transient.yaml &&
gunicorn --bind 0.0.0.0:8000 app.wsgi
#python manage.py runserver 0.0.0.0:8000