#!/bin/env bash

bash entrypoints/wait-for-it.sh database:3306 rabbitmq:5672 celery --timeout=0 &&
celery -A app beat -l INFO