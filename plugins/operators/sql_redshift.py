from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class SQLRedshiftOperator(BaseOperator):

    @apply_defaults
    def __init__(
        self,
        *args,
        redshift_conn_id,
        drop_query,
        create_query,
        insert_query,
        **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.drop_query = drop_query
        self.create_query = create_query
        self.insert_query = insert_query

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)
        redshift_hook.run(self.drop_query)
        redshift_hook.run(self.create_query)
        redshift_hook.run(self.insert_query)
