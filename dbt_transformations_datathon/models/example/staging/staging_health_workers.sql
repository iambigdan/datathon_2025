{{ config(
    materialized = 'table',
    schema = 'mart'
) }}

CREATE TABLE mart_health_workers AS
SELECT
    worker_id,
    facility_id,
    name,
    role,
    qualification,
    CAST(years_experience AS INT) AS years_experience,
    gender,
    specialization,
    shift,
    availability_status
from staging.staging_health_workers