{{ config(
    materialized='table',
    schema='pog_rtip_bronze'
) }}

SELECT
    CAST(event_time AS TIMESTAMP) AS reading_time,
    station_id,
    state,
    fuel_type,
    current_volume,
    tank_capacity,
    utilization_pct

FROM {{ source('bronze', 'raw_tank_readings') }}

