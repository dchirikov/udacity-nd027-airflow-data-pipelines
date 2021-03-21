# nd027: Data Pipelines

## How to run

Before running the pipeline `env.vars` file needs to be created:

Please use `env.vars.template` file as a starting point:

- `REDSHIFT_S3_RO_ROLE` - needed to provide RedShift access to S3 buckets
- `DB_LOGIN`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` and `DB_NAME` credentials for Airflow to get access to the RedShif
- `LOG_BUCKET` and `SONG_BUCKET` name of the buckets with data files

### docker-compose

Just run `make start-airflow` will configure  and run Airflow in autopilot mode. Interface will be available on http://localhost:3000

The only thing needed - is to run pipeline from web-GUI.

### podman-compose

Same as docker-compose, but sysctls tunables might not be configured in proper way, resulting second task (inserting song_data) might hang forever. This caused by long run of the task and lacking TCP keepalive packets.

### On existing Airflow server

Current pipeline requires connector and three variables to be configured:

#### Variables:

- key: `log_bucket`, value: `s3://udacity-dend/log_data`
- key: `song_bucket`, value: `s3://udacity-dend/song_data`
- key: `redshift_s3_ro_role`, value: fully specified ARN: `arn:aws:iam::...`, which provides RedShift RO permissions on S3

#### Connection

The only connections needs to be added is a connection to RedShift database:

- Conn Id: `redshift`
- Conn Type: `postgres`
- Host: FQDN of the hostname where RedShift is available
- Schema: name of the database
- Login: name of the user
- Password: password to access RedShift DB
- Port: 5439

## How to stop

`make stop-airflow` stops containers, but leave database on disk


`make clean-airflow` removes containers and deletes database
