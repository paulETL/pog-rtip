{{ config(
    materialized='table',
    schema='pog_rtip_silver'
) }}

SELECT
    station_id,
    state,
    fuel_type,

    current_volume,

    tank_capacity,

    utilization_pct,

    tank_capacity - current_volume
        AS available_capacity,

    CASE
        WHEN utilization_pct < 20
        THEN TRUE
        ELSE FALSE
    END AS low_tank_flag

FROM {{ ref('bronze_tank_readings') }}

