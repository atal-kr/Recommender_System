#!/bin/bash
# start.sh
#
manage_app () {

    python manage.py makemigrations
    #python manage.py migrate --fake-initial
}

start_development() {
    # use django runserver as development server here.
    manage_app
    uwsgi --http :8001 --chdir /opt/recommender/recommender_service --module recommender_service.wsgi

    }
start_production() {
    # use gunicorn for production server here
    manage_app
    gunicorn recommender_service.wsgi -w 4 -b 0.0.0.0:8001 --chdir=/opt/recommender/recommender_service --log-file -
}
if [ ${PRODUCTION} ]
then
    # use development server
    start_development
else
    # use production server
    echo production
    start_production
fi

