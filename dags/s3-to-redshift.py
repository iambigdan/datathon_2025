from airflow.sdk import dag
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime

@dag(
    start_date=datetime(2025, 10, 8),
    schedule=None,
    catchup=False,
    description="Load multiple S3 files into Redshift tables"
)
def s3_to_redshift():


    truncate_disease_report = SQLExecuteQueryOperator(
        task_id='truncate_disease_report',
        conn_id='redshift_conn',
        sql="TRUNCATE TABLE staging.staging_disease_report;"
    )

    load_disease_report = S3ToRedshiftOperator(
        task_id='load_disease_report',
        s3_bucket='datathon.phc',
        s3_key='raw_data/disease_report_full.csv',
        schema='staging',
        table='staging_disease_report',
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_conn',
        redshift_conn_id='redshift_conn'
    )

    truncate_health_workers = SQLExecuteQueryOperator(
        task_id='truncate_health_workers',
        conn_id='redshift_conn',
        sql="TRUNCATE TABLE staging.staging_health_workers;"
    )

    load_health_workers = S3ToRedshiftOperator(
        task_id='load_health_workers',
        s3_bucket='datathon.phc',
        s3_key='raw_data/health_workers_dataset.csv',
        schema='staging',
        table='staging_health_workers',
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_conn',
        redshift_conn_id='redshift_conn'
    )

    truncate_inventory_dataset = SQLExecuteQueryOperator(
        task_id='truncate_inventory_dataset',
        conn_id='redshift_conn',
        sql="TRUNCATE TABLE staging.staging_inventory_dataset;"
    )

    load_inventory_dataset = S3ToRedshiftOperator(
        task_id='load_inventory_dataset',
        s3_bucket='datathon.phc',
        s3_key='raw_data/inventory_dataset.csv',
        schema='staging',
        table='staging_inventory_dataset',
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_conn',
        redshift_conn_id='redshift_conn'
    )

    truncate_Nigeria_phc = SQLExecuteQueryOperator(
        task_id='truncate_nigeria_phc',
        conn_id='redshift_conn',
        sql="TRUNCATE TABLE staging.staging_nigeria_phc;"
    )

    load_Nigeria_phc = S3ToRedshiftOperator(
        task_id='load_Nigeria_phc',
        s3_bucket='datathon.phc',
        s3_key='raw_data/Nigeria_phc_32000.csv',
        schema='staging',
        table='staging_Nigeria_phc',
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_conn',
        redshift_conn_id='redshift_conn'
    )

    truncate_patients_dataset = SQLExecuteQueryOperator(
        task_id='truncate_patients_dataset',
        conn_id='redshift_conn',
        sql="TRUNCATE TABLE staging.staging_patients_dataset;"
    )

    load_patients_dataset = S3ToRedshiftOperator(
        task_id='load_patients_dataset',
        s3_bucket='datathon.phc',
        s3_key='raw_data/patients_dataset.csv',
        schema='staging',
        table='staging_patients_dataset',
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_conn',
        redshift_conn_id='redshift_conn'
    )

    
    truncate_disease_report >> load_disease_report 
    truncate_health_workers >> load_health_workers
    truncate_inventory_dataset >> load_inventory_dataset 
    truncate_Nigeria_phc >> load_Nigeria_phc 
    truncate_patients_dataset >> load_patients_dataset

s3_to_redshift()
