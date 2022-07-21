#!/bin/env bash
bash entrypoints/wait-for-it.sh database:3306 --timeout=0 &&
bash entrypoints/wait-for-it.sh rabbitmq:5672 --timeout=0 &&
bash entrypoints/wait-for-it.sh app:8000 --timeout=0 &&
celery --broker=amqp://guest:guest@rabbitmq:5672// flower --port=8888
