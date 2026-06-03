"""dbt job - separate from ingestion."""
import os
import subprocess
from dagster import op, job, get_dagster_logger


@op
def run_dbt():
    """Run dbt to transform bronze data into silver and gold layers."""
    logger = get_dagster_logger()
    
    # Get the dbt project directory
    dbt_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "dbt"
    )
    
    logger.info(f"Starting dbt transformations from: {dbt_dir}")
    
    try:
        # Run dbt models
        result = subprocess.run(
            ["dbt", "run", "--profiles-dir", dbt_dir, "--project-dir", dbt_dir],
            cwd=dbt_dir,
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
        
        logger.info("✓ dbt successfully transformed bronze → silver → gold")
        return {"status": "success"}
        
    except subprocess.TimeoutExpired:
        logger.error("dbt run timed out after 10 minutes")
        raise
    except Exception as e:
        logger.error(f"Error running dbt: {str(e)}")
        raise


@job
def dbt_transform_job():
    """Job to run dbt transformations."""
    run_dbt()
