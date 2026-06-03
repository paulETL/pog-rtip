{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    attendant_id,
    station_id,

    COUNT(*) AS fraud_events,

    SUM(estimated_loss) AS total_fraud_loss,

    AVG(variance_liters) AS avg_variance

FROM {{ ref('silver_fraud') }}

WHERE fraud_flag = TRUE

GROUP BY
    attendant_id,
    station_id
