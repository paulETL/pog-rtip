{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    station_id,
    state,
    pump_id,
    health_score,

    CASE
        WHEN health_score < 40 THEN 'CRITICAL'
        WHEN health_score < 60 THEN 'HIGH'
        WHEN health_score < 80 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS failure_risk,

    failure_flag

FROM {{ ref('silver_pump_health') }}
