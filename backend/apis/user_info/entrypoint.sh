#!bin/bash

./wait-for-it.sh db:5432


#python -m pip install --upgrade pip
#python -m pip install --no-cache-dir -r  requirements.txt

#Database migrations

python manage.py makemigrations user_info_app
python manage.py makemigrations
python manage.py migrate

#python manage.py runserver 0.0.0.0:8000
# Run Daphne server

#python manage.py runserver 0.0.0.0:8000
daphne -b 0.0.0.0 -p 8000 user_info.asgi:application