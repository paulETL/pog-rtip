{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    station_id,
    state,
    fuel_type,
    current_volume,
    tank_capacity,
    available_capacity,
    utilization_pct,
    low_tank_flag

FROM {{ ref('silver_inventory') }}
