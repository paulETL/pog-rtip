{{ config(
    materialized='table',
    schema='pog_rtip_bronze'
) }}

SELECT
    event_id,
    CAST(event_time AS TIMESTAMP) AS event_time,
    station_id,
    state,
    pump_id,
    attendant_id,
    shift,
    fuel_type,
    requested_liters,
    actual_dispensed_liters,
    variance_liters,
    unit_price,
    expected_amount,
    actual_amount_paid,
    payment_type,
    fraud_flag

FROM {{ source('bronze', 'raw_pump_transactions') }}

