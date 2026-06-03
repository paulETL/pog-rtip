{{ config(
    materialized='table',
    schema='pog_rtip_silver'
) }}

SELECT
    station_id,
    state,
    latitude,
    longitude,
    pump_count,
    fraud_risk,
    pms_capacity,
    ago_capacity,
    lpg_capacity,
    atk_capacity

FROM {{ ref('bronze_dim_stations') }}

