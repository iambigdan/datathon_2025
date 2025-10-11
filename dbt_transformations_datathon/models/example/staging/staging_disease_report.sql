CREATE TABLE intermediate_disease_report AS
SELECT
    report_id,
    facility_id,
    month VARCHAR,
    disease VARCHAR,
    CAST(cases_reported AS INT) AS cases_reported,
    CAST(deaths AS INT) AS deaths
from staging.staging_disease_report