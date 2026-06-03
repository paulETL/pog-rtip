{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    DATE(event_time) AS sales_date,

    HOUR(event_time) AS sales_hour,

    COUNT(*) AS transaction_count,

    SUM(liters_sold) AS liters_sold,

    SUM(revenue) AS total_revenue

FROM {{ ref('silver_sales') }}

GROUP BY
    DATE(event_time),
    HOUR(event_time)
