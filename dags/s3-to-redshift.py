from airflow.decorators import dag
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from datetime import datetime

@dag(
    start_date=datetime(2025, 10, 8),
    schedule=None,
    catchup=False,
    description="Load multiple S3 files into Redshift tables"
)
def s3_to_redshift():

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

    load_Nigeria_phc = S3ToRedshiftOperator(
        task_id='load_Nigeria_phc',
        s3_bucket='datathon.phc',
        s3_key='raw_data/Nigeria_phc_3200.csv',
        schema='staging',
        table='staging_Nigeria_phc',
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_conn',
        redshift_conn_id='redshift_conn'
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

    
    load_disease_report >> load_health_workers >> load_inventory_dataset >>load_Nigeria_phc >> load_patients_dataset

s3_to_redshift()
