import os
import sys
import logging
from datetime import datetime

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

from pyflink.table import (
    EnvironmentSettings,
    TableEnvironment
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/flink_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

logger.info("=" * 60)
logger.info("Starting Flink Kafka to MinIO Ingestion Job")
logger.info(f"Timestamp: {datetime.now().isoformat()}")
logger.info("=" * 60)

# Validate required environment variables
required_env_vars = ["MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"]
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Missing required environment variable: {var}")
        sys.exit(1)

logger.info(f"MinIO User configured: {os.getenv('MINIO_ROOT_USER')}")

# -------------------------------------------------
# INITIALIZE MinIO BUCKETS
# -------------------------------------------------

def ensure_bucket_exists(bucket_name="pog-rtip-raw", max_retries=30, retry_delay=2):
    """
    Create MinIO bucket if it doesn't exist.
    Uses boto3 S3 client configured for MinIO.
    Retries if MinIO is not yet available.
    """
    import time
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Checking if bucket '{bucket_name}' exists (attempt {attempt + 1}/{max_retries})...")
            
            # Configure boto3 S3 client for MinIO
            s3_client = boto3.client(
                's3',
                endpoint_url='http://minio:9000',
                aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
                aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
                region_name='us-east-1'
            )
            
            # Try to list bucket to check if it exists
            s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' already exists")
            return
            
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            
            if error_code == 404:
                # Bucket doesn't exist, create it
                logger.info(f"Bucket '{bucket_name}' not found. Creating...")
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    logger.info(f"Successfully created bucket '{bucket_name}'")
                    return
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {str(create_error)}")
                    raise
            elif error_code == 403:
                # Access denied
                logger.error(f"Access denied to bucket '{bucket_name}'. Check credentials.")
                raise
            else:
                logger.error(f"Error checking bucket: {str(e)}")
                raise
        except Exception as e:
            # MinIO not ready yet or connection error, retry
            if attempt < max_retries - 1:
                logger.warning(f"Could not connect to MinIO (attempt {attempt + 1}/{max_retries}): {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to MinIO after {max_retries} attempts: {str(e)}")
                raise

# Ensure bucket exists before starting Flink job
logger.info("Initializing MinIO buckets...")
ensure_bucket_exists()
logger.info("MinIO bucket initialization completed")

t_env = TableEnvironment.create(
    EnvironmentSettings.in_streaming_mode()
)

logger.info("TableEnvironment created")

# JAR dependencies are baked into the Docker image via Dockerfile wget
logger.info("JAR dependencies available in container")

# -------------------------------------------------
# MINIO/S3A CONFIG - CORRECT HADOOP S3A PROPERTIES
# -------------------------------------------------

# ============================================================
# MINIO / S3A CONFIGURATION
# ============================================================

# Use MinIO credentials from environment
access_key = os.getenv("MINIO_ROOT_USER")
secret_key = os.getenv("MINIO_ROOT_PASSWORD")

logger.info("Configuring MinIO/S3A...")
logger.info(f"MINIO_ROOT_USER={repr(access_key)}")
logger.info(
    f"MINIO_ROOT_PASSWORD length={len(secret_key) if secret_key else 0}"
)

if not access_key:
    raise RuntimeError("MINIO_ROOT_USER is not set")

if not secret_key:
    raise RuntimeError("MINIO_ROOT_PASSWORD is not set")

flink_config = t_env.get_config()

# Flink translates the s3.* keys into the filesystem-specific configuration
# used by flink-s3-fs-hadoop on the TaskManagers.
for key, value in {
    "execution.checkpointing.interval": "10 s",
    "s3.endpoint": "http://minio:9000",
    "s3.path.style.access": "true",
    "s3.access-key": access_key,
    "s3.secret-key": secret_key,
    "s3.connection.maximum": "100",
    "s3.connection.timeout": "10000",
    "s3.socket.timeout": "10000",
}.items():
    flink_config.set(key, value)

# Keep Hadoop S3A keys as a fallback for the explicit s3a:// sink paths.
for key, value in {
    "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    "fs.s3a.endpoint": "http://minio:9000",
    "fs.s3a.path.style.access": "true",
    "fs.s3a.ssl.enabled": "false",
    "fs.s3a.access.key": access_key,
    "fs.s3a.secret.key": secret_key,
    "fs.s3a.connection.maximum": "100",
    "fs.s3a.connection.timeout": "10000",
    "fs.s3a.socket.timeout": "10000",
}.items():
    flink_config.set(key, value)

logger.info("MinIO/S3A configuration completed")
logger.info("Endpoint: http://minio:9000")
logger.info("Path-style access: enabled")
logger.info("SSL: disabled")

# -------------------------------------------------
# PUMP TRANSACTIONS SOURCE
# -------------------------------------------------

logger.info("Creating pump_transactions source table...")
t_env.execute_sql("""
CREATE TABLE pump_transactions (
    event_id STRING,
    event_time STRING,
    station_id STRING,
    state STRING,
    pump_id STRING,
    attendant_id STRING,
    shift STRING,
    fuel_type STRING,
    requested_liters DOUBLE,
    actual_dispensed_liters DOUBLE,
    variance_liters DOUBLE,
    unit_price DOUBLE,
    expected_amount DOUBLE,
    actual_amount_paid DOUBLE,
    payment_type STRING,
    fraud_flag BOOLEAN
)
WITH (
    'connector' = 'kafka',
    'topic' = 'pump_transactions',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'properties.group.id' = 'flink-pump-transactions',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
)
""")
logger.info("pump_transactions source created")

# -------------------------------------------------
# TANK READINGS SOURCE
# -------------------------------------------------

logger.info("Creating tank_readings source table...")
t_env.execute_sql("""
CREATE TABLE tank_readings (
    event_time STRING,
    station_id STRING,
    state STRING,
    fuel_type STRING,
    current_volume DOUBLE,
    tank_capacity DOUBLE,
    utilization_pct DOUBLE
)
WITH (
    'connector' = 'kafka',
    'topic' = 'tank_readings',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'properties.group.id' = 'flink-tank-readings',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
)
""")
logger.info("tank_readings source created")

# -------------------------------------------------
# PUMP HEALTH SOURCE
# -------------------------------------------------

logger.info("Creating pump_health source table...")
t_env.execute_sql("""
CREATE TABLE pump_health (
    event_time STRING,
    station_id STRING,
    state STRING,
    pump_id STRING,
    temperature DOUBLE,
    pressure DOUBLE,
    vibration DOUBLE,
    uptime_hours DOUBLE,
    failure_flag BOOLEAN
)
WITH (
    'connector' = 'kafka',
    'topic' = 'pump_health',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'properties.group.id' = 'flink-pump-health',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
)
""")
logger.info("pump_health source created")

# -------------------------------------------------
# FUEL DELIVERIES SOURCE
# -------------------------------------------------

logger.info("Creating fuel_deliveries source table...")
t_env.execute_sql("""
CREATE TABLE fuel_deliveries (
    delivery_id STRING,
    event_time STRING,
    station_id STRING,
    state STRING,
    fuel_type STRING,
    supplier STRING,
    delivered_volume DOUBLE,
    tank_capacity DOUBLE,
    post_delivery_volume DOUBLE,
    tanker_plate STRING
)
WITH (
    'connector' = 'kafka',
    'topic' = 'fuel_deliveries',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'properties.group.id' = 'flink-fuel-deliveries',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
)
""")
logger.info("fuel_deliveries source created")

# -------------------------------------------------
# RAW SINK TABLES - MinIO S3A Paths
# -------------------------------------------------

logger.info("Creating MinIO sink tables...")

logger.info("Creating raw_pump_transactions sink...")
t_env.execute_sql("""
CREATE TABLE raw_pump_transactions (
    event_id STRING,
    event_time STRING,
    station_id STRING,
    state STRING,
    pump_id STRING,
    attendant_id STRING,
    shift STRING,
    fuel_type STRING,
    requested_liters DOUBLE,
    actual_dispensed_liters DOUBLE,
    variance_liters DOUBLE,
    unit_price DOUBLE,
    expected_amount DOUBLE,
    actual_amount_paid DOUBLE,
    payment_type STRING,
    fraud_flag BOOLEAN
)
WITH (
    'connector' = 'filesystem',
    'path' = 's3a://pog-rtip-raw/pump_transactions/',
    'format' = 'json',
    'sink.rolling-policy.rollover-interval' = '15 s',
    'sink.rolling-policy.check-interval' = '5 s',
    'sink.parallelism' = '1'
)
""")

logger.info("Creating raw_tank_readings sink...")
t_env.execute_sql("""
CREATE TABLE raw_tank_readings (
    event_time STRING,
    station_id STRING,
    state STRING,
    fuel_type STRING,
    current_volume DOUBLE,
    tank_capacity DOUBLE,
    utilization_pct DOUBLE
)
WITH (
    'connector' = 'filesystem',
    'path' = 's3a://pog-rtip-raw/tank_readings/',
    'format' = 'json',
    'sink.rolling-policy.rollover-interval' = '15 s',
    'sink.rolling-policy.check-interval' = '5 s',
    'sink.parallelism' = '1'
)
""")

logger.info("Creating raw_pump_health sink...")
t_env.execute_sql("""
CREATE TABLE raw_pump_health (
    event_time STRING,
    station_id STRING,
    state STRING,
    pump_id STRING,
    temperature DOUBLE,
    pressure DOUBLE,
    vibration DOUBLE,
    uptime_hours DOUBLE,
    failure_flag BOOLEAN
)
WITH (
    'connector' = 'filesystem',
    'path' = 's3a://pog-rtip-raw/pump_health/',
    'format' = 'json',
    'sink.rolling-policy.rollover-interval' = '15 s',
    'sink.rolling-policy.check-interval' = '5 s',
    'sink.parallelism' = '1'
)
""")

logger.info("Creating raw_fuel_deliveries sink...")
t_env.execute_sql("""
CREATE TABLE raw_fuel_deliveries (
    delivery_id STRING,
    event_time STRING,
    station_id STRING,
    state STRING,
    fuel_type STRING,
    supplier STRING,
    delivered_volume DOUBLE,
    tank_capacity DOUBLE,
    post_delivery_volume DOUBLE,
    tanker_plate STRING
)
WITH (
    'connector' = 'filesystem',
    'path' = 's3a://pog-rtip-raw/fuel_deliveries/',
    'format' = 'json',
    'sink.rolling-policy.rollover-interval' = '15 s',
    'sink.rolling-policy.check-interval' = '5 s',
    'sink.parallelism' = '1'
)
""")

logger.info("All sink tables created successfully")

# -------------------------------------------------
# STREAMING INSERTS - Execute with Error Handling
# -------------------------------------------------

logger.info("Creating streaming insert statements...")

try:
    statement_set = t_env.create_statement_set()

    # Add pump transactions insert
    logger.info("Adding pump_transactions insert...")
    statement_set.add_insert_sql("""
    INSERT INTO raw_pump_transactions
    SELECT * FROM pump_transactions
    """)

    # Add tank readings insert
    logger.info("Adding tank_readings insert...")
    statement_set.add_insert_sql("""
    INSERT INTO raw_tank_readings
    SELECT * FROM tank_readings
    """)

    # Add pump health insert
    logger.info("Adding pump_health insert...")
    statement_set.add_insert_sql("""
    INSERT INTO raw_pump_health
    SELECT * FROM pump_health
    """)

    # Add fuel deliveries insert
    logger.info("Adding fuel_deliveries insert...")
    statement_set.add_insert_sql("""
    INSERT INTO raw_fuel_deliveries
    SELECT * FROM fuel_deliveries
    """)

    logger.info("All insert statements added to statement set")
    logger.info("=" * 60)
    logger.info("STARTING STREAMING INGESTION")
    logger.info("=" * 60)
    logger.info("Data will be written to:")
    logger.info("  - s3a://pog-rtip-raw/pump_transactions/")
    logger.info("  - s3a://pog-rtip-raw/tank_readings/")
    logger.info("  - s3a://pog-rtip-raw/pump_health/")
    logger.info("  - s3a://pog-rtip-raw/fuel_deliveries/")
    logger.info("=" * 60)

    # Execute the streaming job
    statement_set.execute()

except Exception as e:
    logger.error(f"FATAL ERROR during job execution: {str(e)}", exc_info=True)
    sys.exit(1)

