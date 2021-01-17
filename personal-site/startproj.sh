#!bin/bash

source ~/Workspace/Personal/dockerized-personal-site/personal-site/venv/bin/activate

export DEBUG=1
export SECRET_KEY=foo
export DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"

/home/aaroncymor/Workspace/Personal/dockerized-personal-site/personal-site/venv/bin/python manage.py migrate 
/home/aaroncymor/Workspace/Personal/dockerized-personal-site/personal-site/venv/bin/python manage.py runserver

