#!/usr/bin/env bash

ENV=salasvirtuales
NAME=config
DJANGODIR=/apps/salasvirtuales
SOCKFILE=/apps/salasvirtuales/deploy/run/config.sock
NUM_WORKERS=3
TIMEOUT=300
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_WSGI_MODULE=config.wsgi

source /opt/miniconda3/etc/profile.d/conda.sh
conda activate ${ENV}

cd ${DJANGODIR}

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --timeout $TIMEOUT \
  --bind=unix:$SOCKFILE
