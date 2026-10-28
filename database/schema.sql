-- ==============================================================================
-- Electric Vehicle (EV) Market Analysis — Relational Database Schema
-- Database Management System: MySQL 8.0+ / 9.0+
-- Encoding: UTF8MB4 | Collation: utf8mb4_unicode_ci | Storage Engine: InnoDB
-- File: database/schema.sql
-- ==============================================================================

-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS ev_market_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ev_market_db;

-- Safely disable foreign key checks during schema resets
SET FOREIGN_KEY_CHECKS = 0;

DROP VIEW IF EXISTS v_executive_market_kpis;
DROP VIEW IF EXISTS v_manufacturer_market_share;
DROP VIEW IF EXISTS v_battery_performance_summary;
DROP VIEW IF EXISTS v_annual_sales_trends;

DROP TABLE IF EXISTS customer_ratings;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS manufacturing_locations;
DROP TABLE IF EXISTS battery_technologies;
DROP TABLE IF EXISTS manufacturers;

SET FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- 1. Table: manufacturers
-- Holds automotive original equipment manufacturers (OEMs) and corporate groups
-- ==============================================================================
CREATE TABLE manufacturers (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL,
    headquarters_city VARCHAR(100) NOT NULL,
    parent_group VARCHAR(100) NOT NULL,
    founded_year INT NULL,
    is_pure_ev_player BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_mfg_year CHECK (founded_year IS NULL OR founded_year BETWEEN 1800 AND 2030)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_mfg_country ON manufacturers(country);
CREATE INDEX idx_mfg_parent ON manufacturers(parent_group);

-- ==============================================================================
-- 2. Table: battery_technologies
-- Holds battery chemical compositions, electrochemical metrics, and cost baselines
-- ==============================================================================
CREATE TABLE battery_technologies (
    battery_tech_id INT AUTO_INCREMENT PRIMARY KEY,
    chemistry_code VARCHAR(50) NOT NULL UNIQUE,
    chemistry_name VARCHAR(100) NOT NULL,
    cathode_material VARCHAR(100) NOT NULL,
    anode_material VARCHAR(100) NOT NULL,
    nominal_cell_voltage_v DECIMAL(3, 2) NOT NULL,
    energy_density_wh_kg INT NOT NULL,
    cycle_life_cycles INT NOT NULL,
    thermal_stability VARCHAR(50) NOT NULL,
    cost_per_kwh_usd DECIMAL(6, 2) NOT NULL,
    environmental_impact VARCHAR(100) NOT NULL,
    dominant_use_case VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_bat_density CHECK (energy_density_wh_kg > 0 AND energy_density_wh_kg < 1000),
    CONSTRAINT chk_bat_voltage CHECK (nominal_cell_voltage_v > 0.0 AND nominal_cell_voltage_v < 10.0),
    CONSTRAINT chk_bat_cost CHECK (cost_per_kwh_usd > 0.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_bat_density ON battery_technologies(energy_density_wh_kg);

-- ==============================================================================
-- 3. Table: manufacturing_locations
-- Holds global Gigafactories, battery plants, and vehicle assembly facilities
-- ==============================================================================
CREATE TABLE manufacturing_locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT NOT NULL,
    plant_name VARCHAR(150) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    facility_type VARCHAR(100) NOT NULL,
    annual_capacity_units INT NOT NULL,
    operational_since INT NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_loc_mfg FOREIGN KEY (manufacturer_id) 
        REFERENCES manufacturers(manufacturer_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_loc_capacity CHECK (annual_capacity_units >= 0),
    CONSTRAINT chk_loc_year CHECK (operational_since BETWEEN 1900 AND 2030)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_loc_country ON manufacturing_locations(country);
CREATE INDEX idx_loc_region ON manufacturing_locations(region);
CREATE INDEX idx_loc_mfg ON manufacturing_locations(manufacturer_id);

-- ==============================================================================
-- 4. Table: vehicles
-- Holds individual EV models, technical specifications, range, and pricing
-- ==============================================================================
CREATE TABLE vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT NOT NULL,
    model_name VARCHAR(150) NOT NULL,
    variant_name VARCHAR(150) NOT NULL DEFAULT 'Standard',
    model_year INT NOT NULL,
    vehicle_category VARCHAR(50) NOT NULL,
    drivetrain VARCHAR(50) NOT NULL,
    battery_tech_id INT NOT NULL,
    battery_capacity_gross_kwh DECIMAL(6, 2) NOT NULL,
    battery_capacity_net_kwh DECIMAL(6, 2) NOT NULL,
    driving_range_km DECIMAL(6, 2) NOT NULL,
    energy_consumption_wh_km DECIMAL(6, 2) NOT NULL,
    acceleration_0_100_s DECIMAL(4, 2) NOT NULL,
    top_speed_kmh INT NOT NULL,
    dc_max_charge_power_kw DECIMAL(6, 2) NOT NULL,
    ac_max_charge_power_kw DECIMAL(6, 2) NOT NULL,
    charge_time_10_80_min INT NOT NULL,
    base_price_usd DECIMAL(10, 2) NOT NULL,
    origin_country VARCHAR(100) NOT NULL,
    sources TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_veh_mfg FOREIGN KEY (manufacturer_id) 
        REFERENCES manufacturers(manufacturer_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_veh_bat FOREIGN KEY (battery_tech_id) 
        REFERENCES battery_technologies(battery_tech_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_veh_range CHECK (driving_range_km > 0 AND driving_range_km <= 2000),
    CONSTRAINT chk_veh_battery CHECK (battery_capacity_gross_kwh > 0 AND battery_capacity_gross_kwh <= 500),
    CONSTRAINT chk_veh_price CHECK (base_price_usd > 0),
    CONSTRAINT chk_veh_year CHECK (model_year BETWEEN 2010 AND 2030)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_veh_mfg ON vehicles(manufacturer_id);
CREATE INDEX idx_veh_cat ON vehicles(vehicle_category);
CREATE INDEX idx_veh_bat ON vehicles(battery_tech_id);
CREATE INDEX idx_veh_year ON vehicles(model_year);
CREATE INDEX idx_veh_range ON vehicles(driving_range_km);
CREATE INDEX idx_veh_price ON vehicles(base_price_usd);

-- ==============================================================================
-- 5. Table: sales
-- Holds annual market sales, registrations, and growth across regions and OEMs
-- ==============================================================================
CREATE TABLE sales (
    sales_id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    region VARCHAR(100) NOT NULL,
    manufacturer_id INT NULL,
    vehicle_category VARCHAR(50) NOT NULL,
    powertrain VARCHAR(50) NOT NULL,
    units_sold INT NOT NULL,
    market_share_pct DECIMAL(5, 2) NULL,
    yoy_growth_pct DECIMAL(6, 2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_mfg FOREIGN KEY (manufacturer_id) 
        REFERENCES manufacturers(manufacturer_id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_sales_units CHECK (units_sold >= 0),
    CONSTRAINT chk_sales_year CHECK (year BETWEEN 2000 AND 2035)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_sales_year_reg ON sales(year, region);
CREATE INDEX idx_sales_mfg ON sales(manufacturer_id);
CREATE INDEX idx_sales_cat ON sales(vehicle_category);
CREATE INDEX idx_sales_pwrt ON sales(powertrain);

-- ==============================================================================
-- 6. Table: customer_ratings
-- Holds empirical satisfaction benchmarks from automotive consumer studies
-- ==============================================================================
CREATE TABLE customer_ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT NOT NULL,
    vehicle_category VARCHAR(50) NOT NULL,
    survey_year INT NOT NULL,
    sample_size INT NOT NULL,
    overall_score DECIMAL(3, 2) NOT NULL,
    range_satisfaction DECIMAL(3, 2) NOT NULL,
    charging_experience DECIMAL(3, 2) NOT NULL,
    reliability_score DECIMAL(3, 2) NOT NULL,
    build_quality_score DECIMAL(3, 2) NOT NULL,
    software_infotainment_score DECIMAL(3, 2) NOT NULL,
    value_for_money DECIMAL(3, 2) NOT NULL,
    net_promoter_score INT NOT NULL,
    source_note VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rat_mfg FOREIGN KEY (manufacturer_id) 
        REFERENCES manufacturers(manufacturer_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_rat_overall CHECK (overall_score BETWEEN 1.00 AND 5.00),
    CONSTRAINT chk_rat_nps CHECK (net_promoter_score BETWEEN -100 AND 100),
    CONSTRAINT chk_rat_sample CHECK (sample_size > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_rat_mfg ON customer_ratings(manufacturer_id);
CREATE INDEX idx_rat_cat ON customer_ratings(vehicle_category);

-- ==============================================================================
-- ANALYTICAL VIEWS FOR REPORTING & TABLEAU CONNECTOR
-- ==============================================================================

-- View 1: Annual Market Sales & YoY Growth Trends
CREATE OR REPLACE VIEW v_annual_sales_trends AS
SELECT 
    year,
    region,
    vehicle_category,
    powertrain,
    SUM(units_sold) AS total_units_sold,
    AVG(market_share_pct) AS avg_reported_market_share,
    AVG(yoy_growth_pct) AS avg_yoy_growth_pct
FROM sales
GROUP BY year, region, vehicle_category, powertrain;

-- View 2: Manufacturer Global Market Share & Ranking (2023)
CREATE OR REPLACE VIEW v_manufacturer_market_share AS
SELECT 
    m.name AS manufacturer_name,
    m.country AS country_of_origin,
    m.parent_group,
    s.year,
    s.region,
    s.powertrain,
    s.units_sold,
    s.market_share_pct,
    s.yoy_growth_pct,
    RANK() OVER (PARTITION BY s.year, s.region, s.powertrain ORDER BY s.units_sold DESC) AS sales_rank
FROM sales s
JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
WHERE s.manufacturer_id IS NOT NULL;

-- View 3: Battery Performance and Range Statistics by Vehicle Category
CREATE OR REPLACE VIEW v_battery_performance_summary AS
SELECT 
    v.vehicle_category,
    b.chemistry_code,
    b.chemistry_name,
    COUNT(v.vehicle_id) AS total_models,
    ROUND(AVG(v.battery_capacity_gross_kwh), 2) AS avg_battery_gross_kwh,
    ROUND(AVG(v.driving_range_km), 2) AS avg_driving_range_km,
    ROUND(MAX(v.driving_range_km), 2) AS max_driving_range_km,
    ROUND(AVG(v.energy_consumption_wh_km), 2) AS avg_consumption_wh_km,
    ROUND(AVG(v.dc_max_charge_power_kw), 2) AS avg_fast_charge_power_kw,
    ROUND(AVG(v.charge_time_10_80_min), 1) AS avg_charge_time_min,
    ROUND(AVG(v.base_price_usd), 2) AS avg_price_usd
FROM vehicles v
JOIN battery_technologies b ON v.battery_tech_id = b.battery_tech_id
GROUP BY v.vehicle_category, b.chemistry_code, b.chemistry_name;

-- View 4: Executive High-Level Market KPIs
CREATE OR REPLACE VIEW v_executive_market_kpis AS
SELECT 
    (SELECT COUNT(DISTINCT manufacturer_id) FROM manufacturers) AS total_manufacturers,
    (SELECT COUNT(vehicle_id) FROM vehicles) AS total_vehicle_models,
    (SELECT ROUND(AVG(driving_range_km), 1) FROM vehicles) AS avg_driving_range_km,
    (SELECT ROUND(AVG(battery_capacity_gross_kwh), 1) FROM vehicles) AS avg_battery_kwh,
    (SELECT ROUND(AVG(base_price_usd), 0) FROM vehicles) AS avg_vehicle_price_usd,
    (SELECT ROUND(AVG(overall_score), 2) FROM customer_ratings) AS avg_customer_rating,
    (SELECT SUM(units_sold) FROM sales WHERE year = 2023 AND region = 'Global' AND powertrain = 'BEV' AND manufacturer_id IS NULL) AS global_bev_sales_2023;
