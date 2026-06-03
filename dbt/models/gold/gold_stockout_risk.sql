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

    CASE
        WHEN utilization_pct < 10 THEN 'CRITICAL'
        WHEN utilization_pct < 20 THEN 'HIGH'
        WHEN utilization_pct < 40 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS stockout_risk

FROM {{ ref('silver_inventory') }}
