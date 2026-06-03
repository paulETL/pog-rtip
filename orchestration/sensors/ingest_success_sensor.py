"""Sensor to trigger dbt after ingestion job succeeds."""
from dagster import sensor, RunRequest, RunsFilter, DagsterRunStatus, get_dagster_logger


@sensor(job_name="dbt_transform_job")
def ingest_success_sensor(context):
    """Trigger dbt_transform_job after ingest_data_job completes successfully."""
    logger = get_dagster_logger()
    
    instance = context.instance
    
    # Get the most recent run of ingest_data_job
    runs = instance.get_runs(
        filters=RunsFilter(
            statuses=[DagsterRunStatus.SUCCESS],
            job_name="ingest_data_job",
        ),
        limit=1,
    )
    
    if not runs:
        logger.info("No successful ingest_data_job runs found yet")
        return
    
    latest_run = runs[0]
    
    # Use the run ID as the cursor to avoid re-triggering
    if context.cursor == latest_run.run_id:
        logger.info(f"dbt already triggered for ingest run {latest_run.run_id}")
        return
    
    logger.info(f"Ingestion job succeeded (run {latest_run.run_id}), triggering dbt...")
    context.update_cursor(latest_run.run_id)
    
    yield RunRequest(run_key=latest_run.run_id)
