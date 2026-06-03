from dagster import asset

from assets.minio_to_databricks import ingest_dataset


@asset(required_resource_keys={"minio", "databricks"})
def tank_readings(context):

    ingest_dataset(
        context,
        "tank_readings/",
        "workspace.pog_rtip_bronze.raw_tank_readings",
    )
