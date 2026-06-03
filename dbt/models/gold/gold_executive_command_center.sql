{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

WITH sales AS (

    SELECT
        SUM(total_revenue) AS revenue_today,
        SUM(liters_sold) AS liters_sold_today
    FROM {{ ref('gold_sales_daily') }}

),

stations AS (

    SELECT
        COUNT(DISTINCT station_id) AS active_stations
    FROM {{ ref('silver_sales') }}

),

fraud AS (

    SELECT
        SUM(total_fraud_loss) AS fraud_loss_estimate
    FROM {{ ref('gold_fraud_losses') }}

),

inventory AS (

    SELECT
        COUNT(*) AS low_tank_count
    FROM {{ ref('gold_inventory_position') }}
    WHERE low_tank_flag = TRUE

),

maintenance AS (

    SELECT
        SUM(failed_pumps) AS failed_pump_count
    FROM {{ ref('gold_maintenance_scores') }}

)

SELECT
    revenue_today,
    liters_sold_today,
    active_stations,
    fraud_loss_estimate,
    low_tank_count,
    failed_pump_count

FROM sales
CROSS JOIN stations
CROSS JOIN fraud
CROSS JOIN inventory
CROSS JOIN maintenance

