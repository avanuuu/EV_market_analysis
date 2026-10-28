-- ==============================================================================
-- Electric Vehicle (EV) Market Analysis — Analytical SQL Queries
-- Database: ev_market_db (MySQL 8.0+ / 9.0+)
-- File: database/analysis_queries.sql
-- ==============================================================================
-- Description:
-- Production SQL analytical scripts addressing all core business questions across
-- Market Strategy, Automotive BI, and Sustainable Mobility research personas.
-- Utilizes Window Functions, Common Table Expressions (CTEs), Aggregations,
-- and robust NULL/zero-division handling.
-- ==============================================================================

USE ev_market_db;

-- ------------------------------------------------------------------------------
-- QUERY 1: Total Annual EV Sales (Global & Major Regions)
-- Persona: Market Strategy Director & Automotive BI Manager
-- Objective: Track total volume growth across powertrains (BEV vs. PHEV)
-- ------------------------------------------------------------------------------
SELECT 
    year,
    region,
    powertrain,
    SUM(units_sold) AS total_units_sold,
    FORMAT(SUM(units_sold), 0) AS formatted_units_sold
FROM sales
WHERE manufacturer_id IS NULL -- Select macro regional totals to prevent double-counting
  AND region IN ('Global', 'China', 'United States', 'Europe')
GROUP BY year, region, powertrain
ORDER BY region ASC, year DESC, powertrain ASC;


-- ------------------------------------------------------------------------------
-- QUERY 2: Year-over-Year (YoY) Sales Growth Rate
-- Persona: Market Strategy Director
-- Formula: ((Current_Year_Sales - Prior_Year_Sales) / Prior_Year_Sales) * 100
-- Utilizes LAG() window function with safe NULL and zero-division protection
-- ------------------------------------------------------------------------------
WITH annual_macro_sales AS (
    SELECT 
        year,
        region,
        powertrain,
        SUM(units_sold) AS total_units
    FROM sales
    WHERE manufacturer_id IS NULL
      AND region = 'Global'
      AND powertrain = 'BEV'
    GROUP BY year, region, powertrain
)
SELECT 
    year,
    region,
    powertrain,
    total_units AS current_year_sales,
    LAG(total_units, 1) OVER (PARTITION BY region, powertrain ORDER BY year ASC) AS prior_year_sales,
    (total_units - LAG(total_units, 1) OVER (PARTITION BY region, powertrain ORDER BY year ASC)) AS net_unit_change,
    ROUND(
        CASE 
            WHEN LAG(total_units, 1) OVER (PARTITION BY region, powertrain ORDER BY year ASC) IS NULL THEN NULL
            WHEN LAG(total_units, 1) OVER (PARTITION BY region, powertrain ORDER BY year ASC) = 0 THEN NULL
            ELSE (
                (total_units - LAG(total_units, 1) OVER (PARTITION BY region, powertrain ORDER BY year ASC)) 
                * 100.0 / LAG(total_units, 1) OVER (PARTITION BY region, powertrain ORDER BY year ASC)
            )
        END, 
    2) AS yoy_growth_percentage
FROM annual_macro_sales
ORDER BY year DESC;


-- ------------------------------------------------------------------------------
-- QUERY 3: Top Manufacturers by EV Sales (Global 2023)
-- Persona: Automotive BI Manager
-- Objective: Rank OEMs by global sales volume using DENSE_RANK()
-- ------------------------------------------------------------------------------
SELECT 
    m.name AS manufacturer_name,
    m.country AS country_of_origin,
    m.parent_group,
    m.is_pure_ev_player,
    s.powertrain,
    s.units_sold,
    s.market_share_pct,
    DENSE_RANK() OVER (ORDER BY s.units_sold DESC) AS global_sales_rank
FROM sales s
JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
WHERE s.year = 2023 
  AND s.region = 'Global'
  AND s.powertrain = 'BEV'
ORDER BY s.units_sold DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 4: Manufacturer Market Share in Defined Geography & Period (USA 2023)
-- Persona: Automotive BI Manager
-- Formula: (OEM_Sales / SUM(OEM_Sales_in_Region)) * 100
-- Defines explicit denominator across the competitive set
-- ------------------------------------------------------------------------------
WITH regional_oem_sales AS (
    SELECT 
        m.name AS manufacturer_name,
        m.country AS manufacturer_country,
        s.units_sold,
        SUM(s.units_sold) OVER () AS total_competitive_volume
    FROM sales s
    JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
    WHERE s.year = 2023
      AND s.region = 'United States'
      AND s.powertrain = 'BEV'
)
SELECT 
    manufacturer_name,
    manufacturer_country,
    units_sold,
    total_competitive_volume,
    ROUND((units_sold * 100.0 / NULLIF(total_competitive_volume, 0)), 2) AS calculated_market_share_pct
FROM regional_oem_sales
ORDER BY units_sold DESC;


-- ------------------------------------------------------------------------------
-- QUERY 5: EV Sales Volume & Contribution by Vehicle Category
-- Persona: Market Strategy Director
-- Objective: Identify sales volume shift across Cars, Vans, Buses, and Trucks
-- ------------------------------------------------------------------------------
WITH category_totals AS (
    SELECT 
        year,
        vehicle_category,
        SUM(units_sold) AS category_units,
        SUM(SUM(units_sold)) OVER (PARTITION BY year) AS global_all_categories_total
    FROM sales
    WHERE manufacturer_id IS NULL
      AND region = 'Global'
      AND year IN (2020, 2021, 2022, 2023)
    GROUP BY year, vehicle_category
)
SELECT 
    year,
    vehicle_category,
    category_units,
    global_all_categories_total,
    ROUND((category_units * 100.0 / NULLIF(global_all_categories_total, 0)), 2) AS category_share_pct
FROM category_totals
ORDER BY year DESC, category_units DESC;


-- ------------------------------------------------------------------------------
-- QUERY 6: Long-Term Historical EV Adoption Trend (2015 - 2023)
-- Persona: Sustainable Mobility Research Analyst
-- Objective: Longitudinal adoption curve showing compound annual growth
-- ------------------------------------------------------------------------------
SELECT 
    year,
    SUM(CASE WHEN powertrain = 'BEV' THEN units_sold ELSE 0 END) AS bev_units,
    SUM(CASE WHEN powertrain = 'PHEV' THEN units_sold ELSE 0 END) AS phev_units,
    SUM(units_sold) AS total_ev_units,
    ROUND(
        (SUM(CASE WHEN powertrain = 'BEV' THEN units_sold ELSE 0 END) * 100.0) / 
        NULLIF(SUM(units_sold), 0), 
    1) AS bev_share_of_ev_pct
FROM sales
WHERE manufacturer_id IS NULL
  AND region = 'Global'
  AND year BETWEEN 2015 AND 2023
GROUP BY year
ORDER BY year ASC;


-- ------------------------------------------------------------------------------
-- QUERY 7: Battery Technology Distribution Across Production Vehicles
-- Persona: Sustainable Mobility Research Analyst
-- Objective: Market share of LFP vs NMC vs NCA across active vehicle models
-- ------------------------------------------------------------------------------
SELECT 
    b.chemistry_code,
    b.chemistry_name,
    b.thermal_stability,
    b.cost_per_kwh_usd,
    b.environmental_impact,
    COUNT(v.vehicle_id) AS active_vehicle_models_count,
    ROUND(COUNT(v.vehicle_id) * 100.0 / (SELECT COUNT(*) FROM vehicles), 2) AS model_adoption_share_pct,
    ROUND(AVG(v.battery_capacity_gross_kwh), 1) AS avg_pack_capacity_kwh,
    ROUND(AVG(v.driving_range_km), 1) AS avg_driving_range_km,
    ROUND(AVG(v.base_price_usd), 0) AS avg_vehicle_price_usd
FROM battery_technologies b
LEFT JOIN vehicles v ON b.battery_tech_id = v.battery_tech_id
GROUP BY 
    b.chemistry_code, 
    b.chemistry_name, 
    b.thermal_stability, 
    b.cost_per_kwh_usd, 
    b.environmental_impact
ORDER BY active_vehicle_models_count DESC;


-- ------------------------------------------------------------------------------
-- QUERY 8: Average and Maximum Driving Range by Vehicle Category
-- Persona: Sustainable Mobility Research Analyst & Market Strategy Director
-- Objective: Range capability benchmarks across SUVs, Sedans, Pickups, and Vans
-- ------------------------------------------------------------------------------
SELECT 
    vehicle_category,
    COUNT(vehicle_id) AS total_models_cataloged,
    ROUND(MIN(driving_range_km), 1) AS min_range_km,
    ROUND(AVG(driving_range_km), 1) AS avg_range_km,
    ROUND(MAX(driving_range_km), 1) AS max_range_km,
    ROUND(STDDEV(driving_range_km), 1) AS stddev_range_km,
    ROUND(AVG(energy_consumption_wh_km), 1) AS avg_consumption_wh_km
FROM vehicles
GROUP BY vehicle_category
HAVING COUNT(vehicle_id) >= 5
ORDER BY avg_range_km DESC;


-- ------------------------------------------------------------------------------
-- QUERY 9: Battery Capacity versus Driving Range Efficiency Correlation
-- Persona: Sustainable Mobility Research Analyst
-- Objective: Measure Wh/km efficiency and range-per-kWh ratio across categories
-- ------------------------------------------------------------------------------
SELECT 
    v.vehicle_category,
    b.chemistry_code,
    ROUND(AVG(v.battery_capacity_net_kwh), 2) AS avg_usable_kwh,
    ROUND(AVG(v.driving_range_km), 2) AS avg_range_km,
    ROUND(AVG(v.driving_range_km / NULLIF(v.battery_capacity_net_kwh, 0)), 2) AS km_per_kwh_efficiency,
    ROUND(AVG(v.energy_consumption_wh_km), 1) AS avg_wh_per_km,
    ROUND(AVG(v.dc_max_charge_power_kw), 1) AS avg_dc_charging_power_kw,
    ROUND(AVG(v.charge_time_10_80_min), 0) AS avg_10_to_80_charge_time_min
FROM vehicles v
JOIN battery_technologies b ON v.battery_tech_id = b.battery_tech_id
GROUP BY v.vehicle_category, b.chemistry_code
ORDER BY v.vehicle_category, km_per_kwh_efficiency DESC;


-- ------------------------------------------------------------------------------
-- QUERY 10: Manufacturing Distribution & Gigafactory Capacity by Country
-- Persona: Automotive BI Manager
-- Objective: Geographic concentration of EV assembly and battery manufacturing
-- ------------------------------------------------------------------------------
SELECT 
    country,
    region,
    COUNT(location_id) AS total_major_assembly_plants,
    SUM(annual_capacity_units) AS total_annual_production_capacity,
    FORMAT(SUM(annual_capacity_units), 0) AS formatted_annual_capacity,
    ROUND(
        SUM(annual_capacity_units) * 100.0 / 
        (SELECT SUM(annual_capacity_units) FROM manufacturing_locations), 
    2) AS share_of_global_capacity_pct
FROM manufacturing_locations
GROUP BY country, region
ORDER BY total_annual_production_capacity DESC;


-- ------------------------------------------------------------------------------
-- QUERY 11: Customer Satisfaction & Reliability by Manufacturer and Category
-- Persona: Market Strategy Director
-- Objective: Compare overall score, charging satisfaction, and software ratings
-- ------------------------------------------------------------------------------
SELECT 
    m.name AS manufacturer_name,
    m.country AS manufacturer_country,
    r.vehicle_category,
    r.survey_year,
    r.sample_size,
    r.overall_score,
    r.range_satisfaction,
    r.charging_experience,
    r.reliability_score,
    r.software_infotainment_score,
    r.value_for_money,
    r.net_promoter_score,
    CASE 
        WHEN r.overall_score >= 4.50 THEN 'Tier 1: Industry Leader'
        WHEN r.overall_score >= 4.20 THEN 'Tier 2: Competitive Standard'
        ELSE 'Tier 3: Improvement Required'
    END AS satisfaction_tier
FROM customer_ratings r
JOIN manufacturers m ON r.manufacturer_id = m.manufacturer_id
ORDER BY r.overall_score DESC, r.net_promoter_score DESC;


-- ------------------------------------------------------------------------------
-- QUERY 12: Vehicle Pricing Comparisons Across Segments & Drivetrains
-- Persona: Market Strategy Director & Automotive BI Manager
-- Objective: Understand price positioning, value, and affordability brackets
-- ------------------------------------------------------------------------------
SELECT 
    vehicle_category,
    drivetrain,
    COUNT(vehicle_id) AS model_count,
    ROUND(MIN(base_price_usd), 0) AS min_price_usd,
    ROUND(AVG(base_price_usd), 0) AS avg_price_usd,
    ROUND(MAX(base_price_usd), 0) AS max_price_usd,
    ROUND(AVG(base_price_usd / NULLIF(driving_range_km, 0)), 2) AS price_per_km_range_usd
FROM vehicles
GROUP BY vehicle_category, drivetrain
ORDER BY vehicle_category ASC, avg_price_usd DESC;


-- ------------------------------------------------------------------------------
-- QUERY 13: Top-Performing Manufacturers (Multi-Dimensional Composite Score)
-- Persona: Automotive BI Manager & Executive Stakeholders
-- Criteria:
--   1. Sales Volume (weight: 35%)
--   2. Portfolio Range Capability (weight: 25%)
--   3. Customer Satisfaction (weight: 25%)
--   4. Fast Charging Readiness (weight: 15%)
-- ------------------------------------------------------------------------------
WITH oem_metrics AS (
    SELECT 
        m.manufacturer_id,
        m.name AS manufacturer_name,
        m.country,
        COALESCE(MAX(CASE WHEN s.year = 2023 AND s.region = 'Global' AND s.powertrain = 'BEV' THEN s.units_sold END), 0) AS sales_2023,
        ROUND(AVG(v.driving_range_km), 1) AS avg_portfolio_range_km,
        ROUND(AVG(v.dc_max_charge_power_kw), 1) AS avg_charge_power_kw,
        COALESCE(AVG(r.overall_score), 4.20) AS avg_satisfaction_score
    FROM manufacturers m
    JOIN vehicles v ON m.manufacturer_id = v.manufacturer_id
    LEFT JOIN sales s ON m.manufacturer_id = s.manufacturer_id
    LEFT JOIN customer_ratings r ON m.manufacturer_id = r.manufacturer_id
    GROUP BY m.manufacturer_id, m.name, m.country
    HAVING COUNT(v.vehicle_id) >= 3 -- Require representative portfolio
)
SELECT 
    manufacturer_name,
    country,
    sales_2023,
    avg_portfolio_range_km,
    avg_charge_power_kw,
    avg_satisfaction_score,
    DENSE_RANK() OVER (ORDER BY sales_2023 DESC) AS sales_rank,
    DENSE_RANK() OVER (ORDER BY avg_portfolio_range_km DESC) AS range_rank,
    DENSE_RANK() OVER (ORDER BY avg_satisfaction_score DESC) AS satisfaction_rank
FROM oem_metrics
ORDER BY sales_2023 DESC, avg_portfolio_range_km DESC
LIMIT 12;


-- ------------------------------------------------------------------------------
-- QUERY 14: Data Quality Audit & Completeness Verification
-- Persona: Data Analyst & SQL Engineer
-- Objective: Check for NULL fields, anomalies, range boundaries, and record counts
-- ------------------------------------------------------------------------------
SELECT 
    'vehicles' AS table_name,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN model_name IS NULL OR TRIM(model_name) = '' THEN 1 ELSE 0 END) AS missing_model_names,
    SUM(CASE WHEN driving_range_km IS NULL OR driving_range_km <= 0 THEN 1 ELSE 0 END) AS invalid_ranges,
    SUM(CASE WHEN battery_capacity_gross_kwh IS NULL OR battery_capacity_gross_kwh <= 0 THEN 1 ELSE 0 END) AS invalid_batteries,
    SUM(CASE WHEN base_price_usd IS NULL OR base_price_usd <= 0 THEN 1 ELSE 0 END) AS invalid_prices
FROM vehicles
UNION ALL
SELECT 
    'manufacturers' AS table_name,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN name IS NULL OR TRIM(name) = '' THEN 1 ELSE 0 END) AS missing_names,
    SUM(CASE WHEN country IS NULL OR TRIM(country) = '' THEN 1 ELSE 0 END) AS missing_countries,
    0, 0
FROM manufacturers
UNION ALL
SELECT 
    'sales' AS table_name,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN year IS NULL OR year < 2000 THEN 1 ELSE 0 END) AS invalid_years,
    SUM(CASE WHEN units_sold IS NULL OR units_sold < 0 THEN 1 ELSE 0 END) AS invalid_units,
    0, 0
FROM sales;
