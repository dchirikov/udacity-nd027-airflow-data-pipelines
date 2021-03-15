#!/bin/sh

set -ex

# Initialise SQLite DB
[ -f /root/airflow/airflow.db ] || airflow initdb

# add redshift connection
airflow connections add \
    'redshift' \
    --conn-type 'postgres' \
    --conn-login "${DB_LOGIN}" \
    --conn-password "${DB_PASSWORD}" \
    --conn-host "${DB_HOST}" \
    --conn-port "${DB_PORT}" \
    --conn-schema "${DB_NAME}"

# add role variable
echo "
    {
        \"redshift_s3_ro_role\": \"${REDSHIFT_S3_RO_ROLE}\",
        \"log_bucket\": \"${LOG_BUCKET}\",
        \"song_bucket\": \"${SONG_BUCKET}\"
    }
" > /tmp/s3role.json
airflow variables import /tmp/s3role.json

# Start airflow
airflow scheduler --daemon &
sleep 10
airflow webserver --daemon -p 3000 &

set +x
while true; do
    sleep 1
done
