import json
import time

from assets.databricks_loader import execute_insert


def ingest_dataset(
    context,
    prefix,
    table_name,
    max_retries=3,
    retry_delay=5,
):
    raw_bucket = "pog-rtip-raw"
    processed_bucket = "pog-rtip-processed"

    minio = context.resources.minio
    conn = context.resources.databricks
    cursor = conn.cursor()

    total_rows = 0
    total_moved = 0

    objects = list(minio.list_objects(
        raw_bucket,
        prefix=prefix,
        recursive=True,
    ))

    # Filter out temp files
    objects = [
        o for o in objects
        if "_tmp_" not in o.object_name and not o.object_name.endswith("_tmp")
    ]

    if not objects:
        context.log.info(f"No new files found in {prefix}")
        return

    # Sort oldest first
    objects.sort(key=lambda o: o.last_modified)

    context.log.info(f"Found {len(objects)} files to process in {prefix}")

    for obj in objects:

        # Read file with retry
        content = None
        for attempt in range(max_retries):
            try:
                response = minio.get_object(raw_bucket, obj.object_name)
                content = response.read().decode("utf-8").strip()
                response.close()
                response.release_conn()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    context.log.warning(
                        f"MinIO read failed for {obj.object_name} "
                        f"(attempt {attempt + 1}/{max_retries}): {e}. Retrying..."
                    )
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    context.log.error(
                        f"MinIO read failed after {max_retries} attempts "
                        f"for {obj.object_name}: {e}"
                    )
                    raise

        if not content:
            # Move empty files too so they don't pile up
            _move_to_processed(minio, raw_bucket, processed_bucket, obj.object_name, context)
            continue

        rows = []
        for line in content.splitlines():
            if line.strip():
                rows.append(json.loads(line))

        if not rows:
            _move_to_processed(minio, raw_bucket, processed_bucket, obj.object_name, context)
            continue

        context.log.info(
            f"Inserting {len(rows)} rows from {obj.object_name} into {table_name}"
        )

        # Insert with retry
        for attempt in range(max_retries):
            try:
                execute_insert(cursor, table_name, rows)
                conn.commit()
                total_rows += len(rows)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    context.log.warning(
                        f"Insert failed for {obj.object_name} "
                        f"(attempt {attempt + 1}/{max_retries}): {e}. Retrying..."
                    )
                    time.sleep(retry_delay * (attempt + 1))
                    cursor = conn.cursor()
                else:
                    context.log.error(
                        f"Insert failed after {max_retries} attempts "
                        f"for {obj.object_name}: {e}"
                    )
                    raise

        # Only move to processed after confirmed successful insert
        _move_to_processed(minio, raw_bucket, processed_bucket, obj.object_name, context)
        total_moved += 1

    context.log.info(
        f"Done — {total_rows} rows loaded into {table_name}, "
        f"{total_moved} files moved to {processed_bucket}"
    )


def _move_to_processed(minio, raw_bucket, processed_bucket, object_name, context):
    """Copy to processed bucket then delete from raw."""
    from minio.commonconfig import CopySource
    
    if not minio.bucket_exists(processed_bucket):
        minio.make_bucket(processed_bucket)

    minio.copy_object(
        processed_bucket,
        object_name,
        CopySource(raw_bucket, object_name),
    )
    minio.remove_object(raw_bucket, object_name)
    context.log.info(f"Moved {object_name} → {processed_bucket}")