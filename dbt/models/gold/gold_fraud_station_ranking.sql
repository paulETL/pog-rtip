{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    station_id,
    state,

    COUNT(*) AS fraud_events,

    SUM(estimated_loss) AS total_fraud_loss,

    SUM(under_dispensed_liters) AS under_dispensed_liters

FROM {{ ref('silver_fraud') }}

WHERE fraud_flag = TRUE

GROUP BY
    station_id,
    state
