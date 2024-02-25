#!/bin/env bash
export FLOWER_UNAUTHENTICATED_API=true
bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0 &&
bash entrypoints/wait-for-it.sh ${MESSAGE_BROKER_HOST}:${MESSAGE_BROKER_PORT} --timeout=0 &&
bash entrypoints/wait-for-it.sh ${WEB_APP_HOST}:${WEB_APP_PORT} --timeout=0 &&
celery --broker=amqp://${RABBITMQ_USERNAME}:${RABBITMQ_PASSWORD}@${MESSAGE_BROKER_HOST}:${MESSAGE_BROKER_PORT}// flower --port=8888
