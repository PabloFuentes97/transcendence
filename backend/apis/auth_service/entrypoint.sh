#!bin/bash

./wait-for-it.sh db:5432
python -m pip install --upgrade pip
python -m pip install django-debug-toolbar
python -m pip install --no-cache-dir -r requirements.txt 2>&1 | grep -v 'Requirement already satisfied'
#Database migrations
python manage.py makemigrations auth_service_app
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
