#!/bin/env bash

python manage.py makemigrations &&
python manage.py migrate &&
python manage.py test host.tests -v 2