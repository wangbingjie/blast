#!/bin/env bash

bash entrypoints/wait-for-it.sh database:3306 --timeout=0 &&
bash entrypoints/wait-for-it.sh rabbitmq:5672 --timeout=0 &&
bash entrypoints/wait-for-it.sh app:8000 --timeout=0 &&
celery -A app worker -l ERROR --max-memory-per-child 12000
