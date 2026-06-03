{{ config(
    materialized='table',
    schema='pog_rtip_silver'
) }}

SELECT
    health_time,

    station_id,
    state,

    pump_id,

    temperature,
    pressure,
    vibration,

    uptime_hours,

    failure_flag,

    (
        100
        - (temperature * 0.2)
        - (pressure * 0.1)
        - (vibration * 2)
    ) AS health_score

FROM {{ ref('bronze_pump_health') }}

