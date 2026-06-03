{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    attendant_id,

    station_id,

    COUNT(*) AS transaction_count,

    SUM(liters_sold) AS liters_sold,

    SUM(revenue) AS total_revenue,

    AVG(revenue) AS avg_transaction_value

FROM {{ ref('silver_sales') }}

GROUP BY
    attendant_id,
    station_id
