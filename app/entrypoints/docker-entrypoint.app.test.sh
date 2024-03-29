#!/bin/env bash

# Download and install required data
bash entrypoints/initialize_data_dirs.sh
bash entrypoints/initialize_all_data.sh

# Wait for database
bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0 &&

# If .dustmapsrc has been mounted as a read-only file at /tmp/.dustmapsrc,
# copy it to the expected location /root/.dustmapsrc if it does not already exist.
if [[ ! -f "/root/.dustmapsrc" && -f "/tmp/.dustmapsrc" ]]; then
  cp /tmp/.dustmapsrc /root/.dustmapsrc
fi

python manage.py shell < entrypoints/initialize_dustmaps.py &&
coverage run manage.py test host.tests api.tests users.tests -v 2 &&
coverage report -i --omit=host/tests/*,host/migrations/*,app/*,host/urls.py,host/admin.py,host/apps.py,host/__init__.py,manage.py &&
coverage xml -i
