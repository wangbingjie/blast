#!/bin/env bash
bash entrypoints/wait-for-it.sh database:3306 --timeout=0 &&
python manage.py makemigrations &&
python manage.py migrate &&
pip install coverage &&
coverage run manage.py test host.tests -v 2 &&
