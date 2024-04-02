#!/bin/bash

set -eo pipefail

bash entrypoints/initialize_data_dirs.sh

bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0

# If .dustmapsrc has been mounted as a read-only file at /tmp/.dustmapsrc,
# copy it to the expected location /root/.dustmapsrc if it does not already exist.
if [[ ! -f "/root/.dustmapsrc" && -f "/tmp/.dustmapsrc" ]]; then
  cp /tmp/.dustmapsrc /root/.dustmapsrc
fi

INIT_CHECK_FILE=/tmp/initialized/.initialized
if [[ -f "${INIT_CHECK_FILE}" ]]
then
  echo "Application already initialized (\"${INIT_CHECK_FILE}\" exists)."
else
  echo "\"${INIT_CHECK_FILE}\" not found. Running initialization script..."

  # Download and install all required data files
  if [[ "${INITIALIZE_DATA}" == "true" ]]; then
    bash entrypoints/initialize_all_data.sh
  fi

  python entrypoints/init.py

  touch "${INIT_CHECK_FILE}"
fi

echo "Starting server..."
python manage.py runserver 0.0.0.0:${WEB_APP_PORT}
