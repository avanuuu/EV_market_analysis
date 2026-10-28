-- ==============================================================================
-- Electric Vehicle (EV) Market Analysis — Database Validation Scripts
-- Database: ev_market_db (MySQL 8.0+ / 9.0+)
-- File: database/validation_queries.sql
-- ==============================================================================
-- Description:
-- Verifies relational referential integrity, check constraint compliance,
-- boundary values, and validates source-to-database record reconciliation.
-- ==============================================================================

USE ev_market_db;

-- 1. Table Record Counts Reconciliation
SELECT 'manufacturers' AS entity, COUNT(*) AS imported_records, 74 AS expected_records FROM manufacturers
UNION ALL
SELECT 'battery_technologies', COUNT(*), 5 FROM battery_technologies
UNION ALL
SELECT 'manufacturing_locations', COUNT(*), 20 FROM manufacturing_locations
UNION ALL
SELECT 'vehicles', COUNT(*), 1149 FROM vehicles
UNION ALL
SELECT 'sales', COUNT(*), 872 FROM sales
UNION ALL
SELECT 'customer_ratings', COUNT(*), 20 FROM customer_ratings;

-- 2. Foreign Key Orphan Record Audits
-- Must return 0 rows for all checks
SELECT 'Orphan Vehicles (invalid manufacturer_id)' AS check_name, COUNT(*) AS violations
FROM vehicles v
LEFT JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
WHERE m.manufacturer_id IS NULL

UNION ALL

SELECT 'Orphan Vehicles (invalid battery_tech_id)' AS check_name, COUNT(*) AS violations
FROM vehicles v
LEFT JOIN battery_technologies b ON v.battery_tech_id = b.battery_tech_id
WHERE b.battery_tech_id IS NULL

UNION ALL

SELECT 'Orphan Locations (invalid manufacturer_id)' AS check_name, COUNT(*) AS violations
FROM manufacturing_locations l
LEFT JOIN manufacturers m ON l.manufacturer_id = m.manufacturer_id
WHERE m.manufacturer_id IS NULL

UNION ALL

SELECT 'Orphan Ratings (invalid manufacturer_id)' AS check_name, COUNT(*) AS violations
FROM customer_ratings r
LEFT JOIN manufacturers m ON r.manufacturer_id = m.manufacturer_id
WHERE m.manufacturer_id IS NULL;

-- 3. Constraint & Range Boundary Verifications
SELECT 
    'Vehicle Boundary Checks' AS check_name,
    COUNT(*) AS total_checked,
    SUM(CASE WHEN driving_range_km < 20 OR driving_range_km > 1500 THEN 1 ELSE 0 END) AS range_anomalies,
    SUM(CASE WHEN battery_capacity_gross_kwh < 5 OR battery_capacity_gross_kwh > 250 THEN 1 ELSE 0 END) AS battery_anomalies,
    SUM(CASE WHEN base_price_usd < 10000 OR base_price_usd > 3000000 THEN 1 ELSE 0 END) AS price_anomalies,
    SUM(CASE WHEN energy_consumption_wh_km < 80 OR energy_consumption_wh_km > 400 THEN 1 ELSE 0 END) AS efficiency_anomalies
FROM vehicles;

-- 4. Customer Rating Scale Bounds
SELECT 
    'Customer Rating Boundaries' AS check_name,
    COUNT(*) AS total_ratings,
    SUM(CASE WHEN overall_score < 1.00 OR overall_score > 5.00 THEN 1 ELSE 0 END) AS score_out_of_bounds,
    SUM(CASE WHEN net_promoter_score < -100 OR net_promoter_score > 100 THEN 1 ELSE 0 END) AS nps_out_of_bounds
FROM customer_ratings;

-- 5. Sales Data Uniqueness & Consistency
SELECT 
    'Duplicate Sales Keys' AS check_name,
    COUNT(*) AS duplicate_groups
FROM (
    SELECT year, region, COALESCE(manufacturer_id, -1), vehicle_category, powertrain, COUNT(*)
    FROM sales
    GROUP BY year, region, COALESCE(manufacturer_id, -1), vehicle_category, powertrain
    HAVING COUNT(*) > 1
) sub;
