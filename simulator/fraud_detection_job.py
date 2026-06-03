from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.watermark_strategy import WatermarkStrategy

import json


env = StreamExecutionEnvironment.get_execution_environment()

env.set_parallelism(1)


source = KafkaSource.builder() \
    .set_bootstrap_servers("redpanda:9092") \
    .set_topics("pump_transactions") \
    .set_group_id("fraud-detection-job") \
    .set_value_only_deserializer(
        SimpleStringSchema()
    ) \
    .build()


stream = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "Kafka Source"
)


def detect_fraud(record):

    event = json.loads(record)

    variance = event["variance_liters"]

    if variance < -0.05:

        fraud_event = {
            "station_id": event["station_id"],
            "attendant_id": event["attendant_id"],
            "pump_id": event["pump_id"],
            "variance_liters": variance,
            "fraud_score": abs(variance) * 100,
            "fuel_type": event["fuel_type"]
        }

        print(
            f"FRAUD DETECTED: "
            f"{fraud_event}"
        )

    return record


stream.map(detect_fraud)

env.execute("Fraud Detection Job")
