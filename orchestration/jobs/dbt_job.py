"""Jobs - ingestion and dbt transformation."""

import subprocess
from dagster import op, job, get_dagster_logger, define_asset_job, AssetSelection


# ── Ingestion job with max 2 concurrent steps ──────────────────────────────
ingest_data_job = define_asset_job(
    name="ingest_data_job",
    selection=AssetSelection.all(),
    config={
        "execution": {
            "config": {
                "multiprocess": {
                    "max_concurrent": 2
                }
            }
        }
    },
)


# ── dbt job ────────────────────────────────────────────────────────────────
@op
def run_dbt():
    logger = get_dagster_logger()

    project_dir = "/opt/dagster/app/dbt"
    profiles_dir = "/opt/dagster/app"

    logger.info(f"Starting dbt transformations from: {project_dir}")

    try:
        result = subprocess.run(
            [
                "dbt", "run",
                "--project-dir", project_dir,
                "--profiles-dir", profiles_dir,
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
        )

        logger.info(f"dbt run output:\n{result.stdout}")

        if result.returncode != 0:
            logger.error(f"dbt run failed with return code {result.returncode}")
            logger.error(f"dbt run stderr:\n{result.stderr}")
            raise Exception(f"dbt run failed: {result.stderr}")

        logger.info("dbt successfully transformed bronze -> silver -> gold")
        return {"status": "success"}

    except subprocess.TimeoutExpired:
        logger.error("dbt run timed out after 10 minutes")
        raise

    except Exception as e:
        logger.error(f"Error running dbt: {e}")
        raise


@job
def dbt_transform_job():
    run_dbt()