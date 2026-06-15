from dagster import Definitions, define_asset_job
from resources import minio_client, databricks_connection

from assets.station_master import station_master
from assets.pump_transactions import pump_transactions
from assets.tank_readings import tank_readings
from assets.pump_health import pump_health
from assets.fuel_deliveries import fuel_deliveries

from sensors.minio_sensor import minio_sensor
from sensors.ingest_success_sensor import dbt_schedule

from jobs.dbt_job import dbt_transform_job


ingest_data_job = define_asset_job(
    "ingest_data_job",
    selection=[
        station_master,
        pump_transactions,
        tank_readings,
        pump_health,
        fuel_deliveries,
    ],
)

defs = Definitions(
    assets=[
        station_master,
        pump_transactions,
        tank_readings,
        pump_health,
        fuel_deliveries,
    ],
    jobs=[
        ingest_data_job,
        dbt_transform_job,
    ],
    resources={
        "minio": minio_client,
        "databricks": databricks_connection,
    },
    sensors=[
        minio_sensor,
    ],
    schedules=[
        dbt_schedule,
    ],
)