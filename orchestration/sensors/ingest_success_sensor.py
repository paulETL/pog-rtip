"""Run dbt on a fixed schedule."""
from dagster import schedule, RunRequest


@schedule(
    job_name="dbt_transform_job",
    cron_schedule="*/4 * * * *",  # every 4 minutes
)
def dbt_schedule(context):
    """Run dbt every 4 minutes to transform ingested data."""
    return RunRequest()