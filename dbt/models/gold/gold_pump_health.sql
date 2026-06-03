{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    station_id,
    state,
    pump_id,
    health_score,
    temperature,
    pressure,
    vibration,
    uptime_hours,
    failure_flag

FROM {{ ref('silver_pump_health') }}
