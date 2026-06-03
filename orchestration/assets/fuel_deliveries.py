from dagster import asset

from assets.minio_to_databricks import ingest_dataset


@asset(required_resource_keys={"minio", "databricks"})
def fuel_deliveries(context):

    ingest_dataset(
        context,
        "fuel_deliveries/",
        "workspace.pog_rtip_bronze.raw_fuel_deliveries",
    )
