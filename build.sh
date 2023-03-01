#!/usr/bin/env bash
# exit on error
set -o errexit

#python -m pip install --upgrade pip
#pip install -r requirements.txt

# Run React tests
npm run test --prefix frontend
# Build frontend
npm run build --prefix frontend  

# Run Django migrations
python manage.py migrate
# Run Django tests
python manage.py test
# Collect static files for production
python manage.py collectstatic --no-input

# Run app
#python manage.py runserver 0.0.0.0:8000
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 aqi_forecast.wsgi:application