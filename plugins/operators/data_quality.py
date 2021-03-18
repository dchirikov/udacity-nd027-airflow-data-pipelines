from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 *args,
                 redshift_conn_id,
                 songlplays_table,
                 songs_table,
                 users_table,
                 artists_table,
                 time_table,
                 **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.songlplays_table = songlplays_table
        self.songs_table = songs_table
        self.users_table = users_table
        self.artists_table = artists_table
        self.time_table = time_table

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)
        tables = [
            self.songlplays_table,
            self.songs_table,
            self.users_table,
            self.artists_table,
            self.time_table,
        ]
        for table in tables:
            self.check_not_empty(table, redshift_hook)

    def check_not_empty(self, table, redshift_hook):
        query = f"SELECT COUNT(*) FROM {table}"
        records = redshift_hook.get_records(query)
        if len(records) < 1 or len(records[0]) < 1:
            msg = f"Data quality check failed. {table} returned no results"
            raise ValueError(msg)
        num_records = records[0][0]
        if num_records < 1:
            msg = f"Data quality check failed. {table} contained 0 rows"
            raise ValueError(msg)
        msg = f"Data quality on table {table} check passed"
        msg += f" with {records[0][0]} records"
        self.log.info(msg)
