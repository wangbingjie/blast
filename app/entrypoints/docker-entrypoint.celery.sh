#!/bin/env bash

bash entrypoints/wait-for-it.sh database:3306 rabbitmq:5672 --timeout=0 &&
celery -A app worker -l INFO --max-memory-per-child 12000

