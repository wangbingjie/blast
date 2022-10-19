#!/bin/env bash
bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0 &&
#python manage.py makemigrations &&
#python manage.py migrate &&
python manage.py shell < entrypoints/initialize_dustmaps.py &&
coverage run manage.py test host.tests api.tests -v 2 &&
coverage report -i --omit=host/tests/*,host/migrations/*,app/*,host/urls.py,host/admin.py,host/apps.py,host/__init__.py,manage.py &&
coverage xml -i

