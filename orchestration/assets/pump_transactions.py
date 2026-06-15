from dagster import asset

from assets.minio_to_databricks import ingest_dataset

@asset(required_resource_keys={"minio", "databricks"})
def pump_transactions(context):

    ingest_dataset(
        context,
        "pump_transactions/",
        "workspace.pog_rtip_bronze.raw_pump_transactions",
    )
