#!/bin/env bash

set -e

bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0
bash entrypoints/wait-for-it.sh ${MESSAGE_BROKER_HOST}:${MESSAGE_BROKER_PORT} --timeout=0
bash entrypoints/wait-for-it.sh ${WEB_APP_HOST}:${WEB_APP_PORT} --timeout=0

# If .dustmapsrc has been mounted as a read-only file at /tmp/.dustmapsrc,
# copy it to the expected location /root/.dustmapsrc if it does not already exist.
if [[ ! -f "/root/.dustmapsrc" && -f "/tmp/.dustmapsrc" ]]; then
  cp /tmp/.dustmapsrc /root/.dustmapsrc
fi

bash entrypoints/initialize_data_dirs.sh

if [[ $DEV_MODE == 1 ]]; then
  watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- \
  celery -A app worker -l DEBUG --max-memory-per-child ${CELERY_MAX_MEMORY_PER_CHILD:-12000}
else
  celery -A app worker -l ERROR --max-memory-per-child ${CELERY_MAX_MEMORY_PER_CHILD:-12000}
fi
