from dagster import (
    sensor,
    RunRequest,
    RunsFilter,
    DagsterRunStatus,
)


@sensor(
    job_name="ingest_data_job",
    minimum_interval_seconds=120,   # check every 2 mins, not 1
    required_resource_keys={"minio"},
)
def minio_sensor(context):
    minio = context.resources.minio

    # Don't trigger if a run is already active
    active_runs = context.instance.get_runs(
        filters=RunsFilter(
            job_name="ingest_data_job",
            statuses=[
                DagsterRunStatus.STARTED,
                DagsterRunStatus.QUEUED,
                DagsterRunStatus.STARTING,
            ],
        )
    )

    if active_runs:
        context.log.info("Skipping — ingest_data_job already running")
        return

    objects = list(
        minio.list_objects(
            "pog-rtip-raw",
            recursive=True,
        )
    )

    if not objects:
        return

    # Filter out temp files before finding latest
    objects = [
        o for o in objects
        if "_tmp_" not in o.object_name and not o.object_name.endswith("_tmp")
    ]

    if not objects:
        return

    latest = max(objects, key=lambda x: x.last_modified)

    if context.cursor == latest.object_name:
        return

    context.update_cursor(latest.object_name)
    context.log.info(f"New data detected: {latest.object_name}, triggering ingest...")

    yield RunRequest(run_key=latest.object_name)