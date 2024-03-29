#!/bin/env bash

bash entrypoints/initialize_data_dirs.sh
bash entrypoints/initialize_all_data.sh
bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0 &&
python manage.py shell < entrypoints/initialize_dustmaps.py &&
coverage run manage.py test host.tests api.tests users.tests -v 2 &&
coverage report -i --omit=host/tests/*,host/migrations/*,app/*,host/urls.py,host/admin.py,host/apps.py,host/__init__.py,manage.py &&
coverage xml -i
