CREATE TABLE intermediate_patients_dataset AS
SELECT
    patient_id,
    facility_id,
    gender,
    CAST(age AS INT) AS age,
    CAST(visit_date AS DATE) AS visit_date,
    diagnosis,
    treatment,
    outcome
from staging.staging_patients_dataset