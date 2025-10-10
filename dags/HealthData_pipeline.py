from datetime import datetime, timedelta
from airflow.decorators import task
from airflow import DAG






@task
def s3_to_postgres():
