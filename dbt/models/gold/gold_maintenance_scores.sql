{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    station_id,
    state,

    COUNT(*) AS pump_count,

    AVG(health_score) AS avg_health_score,

    SUM(
        CASE
            WHEN failure_flag = TRUE THEN 1
            ELSE 0
        END
    ) AS failed_pumps

FROM {{ ref('silver_pump_health') }}

GROUP BY
    station_id,
    state
