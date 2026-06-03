{{ config(
    materialized='table',
    schema='pog_rtip_bronze'
) }}

SELECT
    delivery_id,
    CAST(event_time AS TIMESTAMP) AS delivery_time,
    station_id,
    state,
    fuel_type,
    supplier,
    delivered_volume,
    tank_capacity,
    post_delivery_volume,
    tanker_plate

FROM {{ source('bronze', 'raw_fuel_deliveries') }}

