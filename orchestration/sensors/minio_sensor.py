from dagster import sensor, RunRequest


@sensor(
    job_name="ingest_data_job",
    minimum_interval_seconds=60,
    required_resource_keys={"minio"},
)
def minio_sensor(context):

    minio = context.resources.minio

    objects = list(
        minio.list_objects(
            "pog-rtip-raw",
            recursive=True,
        )
    )

    if not objects:
        return

    latest = max(
        objects,
        key=lambda x: x.last_modified,
    )

    if context.cursor == latest.object_name:
        return

    context.update_cursor(
        latest.object_name
    )

    yield RunRequest(
        run_key=latest.object_name
    )
