from dagster import asset

from assets.minio_to_databricks import ingest_dataset


@asset(required_resource_keys={"minio", "databricks"})
def pump_health(context):

    ingest_dataset(
        context,
        "pump_health/",
        "workspace.pog_rtip_bronze.raw_pump_health",
    )
