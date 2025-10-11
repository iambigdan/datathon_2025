CREATE TABLE intermediate_inventory_dataset AS
SELECT
    item_id VARCHAR,
    facility_id VARCHAR,
    item_name VARCHAR,
    CAST(stock_level AS INT) AS stock_level,
    CAST(reorder_level AS INT) AS reorder_level,
    CAST(last_restock_date AS date) AS last_restock_date
from staging.staging_inventory_dataset