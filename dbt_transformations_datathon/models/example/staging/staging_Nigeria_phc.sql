CREATE TABLE intermediate_Nigeria_phc AS
SELECT
    facility_id,
    facility_name,
    state,
    lga,
    ownership,
    type,
    CAST(latitude AS FLOAT) AS latitude,
    CAST(longitude AS FLOAT) AS longitude,
    operational_status,
    CAST(number_of_beds AS INT) AS number_of_beds,
    CAST(average_daily_patients AS INT) AS average_daily_patients,
    CAST(health_workers AS INT) AS health_workers
from staging.staging_Nigeria_phc