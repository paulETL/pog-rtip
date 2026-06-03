{{ config(
    materialized='table',
    schema='pog_rtip_silver'
) }}

SELECT
    event_id,
    event_time,

    station_id,
    state,

    attendant_id,
    pump_id,

    shift,
    fuel_type,

    actual_dispensed_liters AS liters_sold,

    unit_price,

    actual_amount_paid AS revenue,

    payment_type,

    fraud_flag

FROM {{ ref('bronze_pump_transactions') }}

