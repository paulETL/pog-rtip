import json

from assets.databricks_loader import execute_insert


def ingest_dataset(
    context,
    prefix,
    table_name,
):

    bucket = "pog-rtip-raw"

    minio = context.resources.minio
    conn = context.resources.databricks

    cursor = conn.cursor()

    all_rows = []

    objects = minio.list_objects(
        bucket,
        prefix=prefix,
        recursive=True,
    )

    for obj in objects:
        # Skip temporary files from Spark/Flink writes
        if "_tmp_" in obj.object_name or obj.object_name.endswith("_tmp"):
            context.log.debug(f"Skipping temporary file: {obj.object_name}")
            continue

        response = minio.get_object(
            bucket,
            obj.object_name,
        )

        content = (
            response.read()
            .decode("utf-8")
            .strip()
        )

        if not content:
            continue

        for line in content.splitlines():

            row = json.loads(line)

            all_rows.append(row)

    execute_insert(
        cursor,
        table_name,
        all_rows,
    )

    conn.commit()

    context.log.info(
        f"{len(all_rows)} rows loaded into {table_name}"
    )
