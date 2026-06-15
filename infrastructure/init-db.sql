-- ============================================================
-- ClickHouse Init Script
-- Runs once on first container start (idempotent: IF NOT EXISTS)
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS pog;

-- ============================================================
-- fact_transactions  (consumer.py)
-- ============================================================
CREATE TABLE IF NOT EXISTS pog.fact_transactions
(
    event_id              String,
    timestamp             DateTime,

    station_id            String,
    state                 String,

    pump_id               String,
    attendant_id          String,
    shift                 String,

    fuel_type             String,

    requested_liters      Float64,
    actual_dispensed_liters Float64,
    variance_liters       Float64,

    unit_price            Float64,

    expected_amount       Float64,
    actual_amount_paid    Float64,

    payment_type          String,

    fraud_flag            UInt8
)
ENGINE = MergeTree()
ORDER BY (timestamp, station_id, pump_id)
PARTITION BY toYYYYMM(timestamp);

-- ============================================================
-- fact_fuel_deliveries  (delivery_consumer.py)
-- ============================================================
CREATE TABLE IF NOT EXISTS pog.fact_fuel_deliveries
(
    timestamp             DateTime,
    delivery_id           String,

    station_id            String,
    state                 String,

    fuel_type             String,
    supplier              String,

    delivered_volume      Float64,
    tank_capacity         Float64,
    post_delivery_volume  Float64,

    tanker_plate          String
)
ENGINE = MergeTree()
ORDER BY (timestamp, station_id, fuel_type)
PARTITION BY toYYYYMM(timestamp);

-- ============================================================
-- fraud_transactions  (fraud_consumer.py)
-- ============================================================
CREATE TABLE IF NOT EXISTS pog.fraud_transactions
(
    timestamp             DateTime,

    station_id            String,
    state                 String,

    attendant_id          String,
    pump_id               String,

    fuel_type             String,

    requested_liters      Float64,
    actual_dispensed_liters Float64,
    variance_liters       Float64,

    expected_amount       Float64,
    actual_amount_paid    Float64,

    fraud_score           Float64,
    fraud_reason          String
)
ENGINE = MergeTree()
ORDER BY (timestamp, station_id, pump_id)
PARTITION BY toYYYYMM(timestamp);

-- ============================================================
-- fact_pump_health  (pump_health_consumer.py)
-- ============================================================
CREATE TABLE IF NOT EXISTS pog.fact_pump_health
(
    timestamp             DateTime,

    station_id            String,
    state                 String,

    pump_id               String,

    temperature           Float64,
    pressure              Float64,
    vibration             Float64,
    uptime_hours          Float64,

    failure_flag          UInt8
)
ENGINE = MergeTree()
ORDER BY (timestamp, station_id, pump_id)
PARTITION BY toYYYYMM(timestamp);

-- ============================================================
-- fact_tank_readings  (tank_consumer.py)
-- ============================================================
CREATE TABLE IF NOT EXISTS pog.fact_tank_readings
(
    timestamp             DateTime,

    station_id            String,
    state                 String,

    fuel_type             String,

    current_volume        Float64,
    tank_capacity         Float64,
    utilization_pct       Float64
)
ENGINE = MergeTree()
ORDER BY (timestamp, station_id, fuel_type)
PARTITION BY toYYYYMM(timestamp);