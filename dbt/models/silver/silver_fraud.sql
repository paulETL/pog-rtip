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

    fuel_type,

    fraud_flag,

    requested_liters,
    actual_dispensed_liters,

    variance_liters,

    expected_amount,
    actual_amount_paid,

    ABS(expected_amount - actual_amount_paid)
        AS estimated_loss,

    requested_liters - actual_dispensed_liters
        AS under_dispensed_liters,

    CASE
        WHEN ABS(variance_liters) >= 10 THEN 'HIGH'
        WHEN ABS(variance_liters) >= 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS fraud_severity

FROM {{ ref('bronze_pump_transactions') }}




