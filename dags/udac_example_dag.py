from datetime import datetime, timedelta
import os
from helpers import SqlQueries
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator)

AWS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'udacity',
    'start_date': datetime.utcnow(),
    # The DAG does not have dependencies on past runs
    'depends_on_past': False,
    # On failure, the task are retried 3 times
    'retries': 3,
    # Retries happen every 5 minutes
    'retry_delay': timedelta(minutes=5),
    # Catchup is turned off
    'catchup': False,
    # Do not email on retry
    'email_on_retry': False,

    'email_on_failure': False,
}

dag = DAG(
    'udac_example_dag',
    default_args=default_args,
    description='Load and transform data in Redshift with Airflow',
    schedule_interval='@monthly'
)

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="staging_events"
    ),
    create_query=SqlQueries.staging_events_table_create.format(
        table="staging_events"
    ),
    insert_query=SqlQueries.staging_insert_query.format(
        table="staging_events",
        bucket=Variable.get("log_bucket"),
        arn=Variable.get("redshift_s3_ro_role")
    )
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="staging_songs"
    ),
    create_query=SqlQueries.staging_songs_table_create.format(
        table="staging_songs"
    ),
    insert_query=SqlQueries.staging_insert_query.format(
        table="staging_songs",
        bucket=Variable.get("song_bucket"),
        arn=Variable.get("redshift_s3_ro_role")
    )
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="songplays"
    ),
    create_query=SqlQueries.songplays_table_create.format(
        table="songplays"
    ),
    insert_query=SqlQueries.songplay_table_insert.format(
        table="songplays",
        staging_events_table="staging_events",
        staging_songs_table="staging_songs",
    )
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="users"
    ),
    create_query=SqlQueries.user_table_create.format(
        table="users"
    ),
    insert_query=SqlQueries.user_table_insert.format(
        table="users",
        staging_events_table="staging_events",
    )
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="songs"
    ),
    create_query=SqlQueries.song_table_create.format(
        table="songs"
    ),
    insert_query=SqlQueries.song_table_insert.format(
        table="songs",
        staging_songs_table="staging_songs",
    )
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="artists"
    ),
    create_query=SqlQueries.artist_table_create.format(
        table="artists"
    ),
    insert_query=SqlQueries.artist_table_insert.format(
        table="artists",
        staging_songs_table="staging_songs",
    )
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    drop_query=SqlQueries.drop_query.format(
        table="time"
    ),
    create_query=SqlQueries.time_table_create.format(
        table="time"
    ),
    insert_query=SqlQueries.time_table_insert.format(
        table="time",
        songplays_table="songplays",
    )
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    songlplays_table="songplays",
    songs_table="songs",
    users_table="users",
    artists_table="artists",
    time_table="time"
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift

stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table

load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks

run_quality_checks >> end_operator
