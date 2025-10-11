Overview
========
Data Engineering Pipeline — Datafest Hackathon 2025 (Team XYZ)

This project implements a data engineering pipeline that automates the flow of raw data from Amazon S3 into Amazon Redshift, transforms it using dbt (Data Build Tool), and orchestrates the entire process with Apache Airflow.

Architecture


s3-to-redshift.py: Copies CSV files from S3 to Redshift staging tables using S3ToRedshiftOperator.

dbt_transformations.py: Triggers dbt transformations after data load completion.

dbt: Cleans, models, and materializes data into analytics-ready schemas.


Tech Stack

Orchestration: Apache Airflow
Transformation: dbt + Redshift
Storage: AWS S3
Data Warehouse: Amazon Redshift Serverless
Environment: WSL (Ubuntu)

Project Contents
================

This project contains some important files and folders:

- dags: This folder contains the Python files for Airflow DAGs:
    - `s3-to-redshift.py`: This DAG automates the process of moving raw data from Amazon s3 bucket into Amazon redshift, and into staging schema for later transformation.
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- requirements.txt: This was used to install important requireents like amazon and Postgres providers. Without then, airflow can not connect to these services
- dbt_env: This folder contains the virtual environment for dbt.It isolates all dbt related dependencies from the main Airflow environment, ensuring clean version management and reproducible builds. Please note that it is system-specific. It was Created using:  
 ```
  python3 -m venv dbt_env.

```
Activated with:
  source dbt_env/bin/activate
Deactivated with:
  deactivate

- dbt_transformations_datathon: This is the part responsible for transforming and modeling data in Amazon Redshift after Airflow has ingested to staging schema.


Deploy Your Project Locally
===========================

Start Airflow on your local machine by running 'astro dev start'.

This command will spin up five Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- DAG Processor: The Airflow component responsible for parsing DAGs
- API Server: The Airflow component responsible for serving the Airflow UI and API
- Triggerer: The Airflow component responsible for triggering deferred tasks

When all five containers are ready the command will open the browser to the Airflow UI at http://localhost:8080/. You should also be able to access your Postgres Database at 'localhost:5432/postgres' with username 'postgres' and password 'postgres'.

Note: If you already have either of the above ports allocated, you can either [stop your existing Docker containers or change the port](https://www.astronomer.io/docs/astro/cli/troubleshoot-locally#ports-are-not-available-for-my-local-airflow-webserver).

Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://www.astronomer.io/docs/astro/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support.
