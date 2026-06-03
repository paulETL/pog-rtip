{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    DATE(event_time) AS fraud_date,

    COUNT(*) AS fraud_events,

    SUM(estimated_loss) AS total_fraud_loss,

    SUM(under_dispensed_liters) AS total_under_dispensed_liters

FROM {{ ref('silver_fraud') }}

WHERE fraud_flag = TRUE

GROUP BY
    DATE(event_time)
