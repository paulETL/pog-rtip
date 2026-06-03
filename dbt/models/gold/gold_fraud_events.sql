{{ config(
    materialized='table',
    schema='pog_rtip_gold'
) }}

SELECT
    event_time,
    station_id,
    state,
    attendant_id,
    pump_id,
    fuel_type,
    fraud_flag,
    variance_liters,
    under_dispensed_liters,
    estimated_loss,
    fraud_severity

FROM {{ ref('silver_fraud') }}
