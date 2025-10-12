from airflow import DAG
from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(
    dag_id="trigger_dbt",
    start_date=datetime(2025, 10, 9),
    schedule=None,
    catchup=False,
    description="DAG to trigger dbt transformations after loading data into Redshift"
)
def trigger_dbt():
    
    run_dbt = BashOperator(
        task_id="run_dbt_models",
        bash_command=(
            "source ../dbt_env/bin/activate && "
            "cd dbt_transformations_datathon && "
            "dbt run"
        ),
    )

    run_dbt

trigger_dbt()
# The above DAG triggers dbt transformations after data is loaded into Redshift.