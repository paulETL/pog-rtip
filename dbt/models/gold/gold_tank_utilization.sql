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

    utilization_pct,

    ROUND(
        (current_volume / tank_capacity) * 100,
        2
    ) AS utilization_percent

FROM {{ ref('silver_inventory') }}
