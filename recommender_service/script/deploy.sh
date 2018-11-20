#!/bin/bash

if [ $# -lt 1 ]
then
    echo "Usage: deploy host [user] [env]"
    exit 1
fi

HOST=$1
USER=${2:-root}

echo "Deploying on $HOST using username $USER"
fab -f script/fabfile.py -H $HOST -u $USER deploy

# Different values for variables can be supplied like-
#fab -f scripts/fabfile.py -H $HOST -u $USER deploy:install_config=no,apache_service=httpd

# To enforce only HTTPS
#fab -f scripts/fabfile.py -H $HOST -u $USER deploy:ssl_only=yes