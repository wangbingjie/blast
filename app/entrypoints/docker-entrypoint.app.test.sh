#!/bin/env bash
bash entrypoints/wait-for-it.sh database:3306 --timeout=0 &&
python manage.py makemigrations &&
python manage.py migrate &&
python manage.py test host.tests -v 2 &&
