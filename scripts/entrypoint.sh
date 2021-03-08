#!/bin/sh

set -ex
# Initialise SQLite DB
[ -f /root/airflow/airflow.db ] || airflow initdb

# Start airflow
airflow scheduler --daemon &
sleep 10
airflow webserver --daemon -p 3000 &
sleep 10

while true; do
    sleep 1
done
