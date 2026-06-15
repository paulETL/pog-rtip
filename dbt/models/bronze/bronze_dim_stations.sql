{{ config(
    materialized='table',
    schema='pog_rtip_bronze',
    pre_hook="TRUNCATE TABLE {{ this }}"
) }}

WITH tank_capacity AS (

    SELECT
        station_id,
        MAX(CASE WHEN fuel_type = 'PMS' THEN tank_capacity END) AS pms_capacity,
        MAX(CASE WHEN fuel_type = 'AGO' THEN tank_capacity END) AS ago_capacity,
        MAX(CASE WHEN fuel_type = 'LPG' THEN tank_capacity END) AS lpg_capacity,
        MAX(CASE WHEN fuel_type = 'ATK' THEN tank_capacity END) AS atk_capacity

    FROM {{ source('bronze','raw_station_tank_capacity') }}
    GROUP BY station_id

)

SELECT
    s.station_id,
    s.state,
    s.latitude,
    s.longitude,
    s.pump_count,
    s.fraud_risk,
    t.pms_capacity,
    t.ago_capacity,
    t.lpg_capacity,
    t.atk_capacity

FROM {{ source('bronze','raw_station_master') }} s
LEFT JOIN tank_capacity t
    ON s.station_id = t.station_id

