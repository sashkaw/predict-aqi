#!/usr/bin/env bash
# exit on error
set -o errexit

#python -m pip install --upgrade pip
#pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input
#python manage.py runserver 0.0.0.0:8000

exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 aqi_forecast.wsgi:application