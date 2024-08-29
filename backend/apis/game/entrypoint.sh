#!bin/bash

python /usr/bin/connect_postgres.py

#Database migrations
python manage.py makemigrations
python manage.py migrate
#python manage.py collectstatic --noinput --clear
python manage.py runserver 0.0.0.0:8000
