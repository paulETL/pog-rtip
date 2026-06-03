{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    DATE(event_time) AS sales_date,

    fuel_type,

    COUNT(*) AS transaction_count,

    SUM(liters_sold) AS liters_sold,

    SUM(revenue) AS total_revenue,

    AVG(revenue) AS avg_transaction_value

FROM {{ ref('silver_sales') }}

GROUP BY
    DATE(event_time),
    fuel_type
