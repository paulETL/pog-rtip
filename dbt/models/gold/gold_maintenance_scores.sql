{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

WITH latest_health AS (

    SELECT *

    FROM (

        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY station_id, pump_id
                ORDER BY health_time DESC
            ) AS rn

        FROM {{ ref('silver_pump_health') }}

    )

    WHERE rn = 1

)

SELECT
    station_id,
    state,

    COUNT(DISTINCT pump_id) AS pump_count,

    AVG(health_score) AS avg_health_score,

    SUM(
        CASE
            WHEN failure_flag = TRUE THEN 1
            ELSE 0
        END
    ) AS failed_pumps

FROM latest_health

GROUP BY
    station_id,
    state
