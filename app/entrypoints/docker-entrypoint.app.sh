#!/bin/env bash

bash entrypoints/wait-for-it.sh "${DB_HOST}":3306 --timeout=0 &&
bash entrypoints/wait-for-it.sh "${FILESERVER_HOST}":80 --timeout=0 &&
python manage.py makemigrations &&
python manage.py migrate &&
bash entrypoints/load_initial_data.sh &&
bash entrypoints/load_example_data.sh &&
#python manage.py loaddata setup_survey_data.yaml &&
#python manage.py loaddata setup_filter_data.yaml &&
#python manage.py loaddata setup_catalog_data.yaml &&
#python manage.py loaddata setup_test_host.yaml &&
#python manage.py loaddata setup_test_transient.yaml &&
#python manage.py loaddata setup_test_cutout.yaml &&
#python manage.py loaddata setup_tasks.yaml &&
#python manage.py loaddata setup_status.yaml &&
#python manage.py loaddata setup_test_cutout.yaml &&
gunicorn app.wsgi:application --bind 0.0.0.0:8000
