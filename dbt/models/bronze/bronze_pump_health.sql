{{ config(
    materialized='table',
    schema='pog_rtip_bronze'
) }}

SELECT
    CAST(event_time AS TIMESTAMP) AS health_time,
    station_id,
    state,
    pump_id,
    temperature,
    pressure,
    vibration,
    uptime_hours,
    failure_flag

FROM {{ source('bronze', 'raw_pump_health') }}

