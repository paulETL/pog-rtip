from confluent_kafka import Producer

from datetime import datetime

import random
import json

# redpanda
producer = Producer({
    "bootstrap.servers": "redpanda:9092"
})


def generate_pump_health(
    stations
):

    for station in stations:

        for pump_num in range(
            1,
            station["pump_count"] + 1
        ):

            temperature = round(
                random.uniform(30, 95),
                2
            )

            pressure = round(
                random.uniform(40, 120),
                2
            )

            vibration = round(
                random.uniform(0.1, 5.0),
                2
            )

            uptime_hours = round(
                random.uniform(100, 5000),
                2
            )

            failure_probability = 0.01

            failure_flag = (
                random.random()
                < failure_probability
            )

            event = {

                "timestamp": (
                    datetime.now().isoformat()
                ),

                "station_id": (
                    station["station_id"]
                ),

                "state": (
                    station["state"]
                ),

                "pump_id": (
                    f"pump_{pump_num}"
                ),

                "temperature": (
                    temperature
                ),

                "pressure": (
                    pressure
                ),

                "vibration": (
                    vibration
                ),

                "uptime_hours": (
                    uptime_hours
                ),

                "failure_flag": (
                    failure_flag
                )
            }

            producer.produce(
                "pump_health",
                json.dumps(event).encode(
                    "utf-8"
                )
            )

    producer.flush()

    print(
        "Pump health telemetry emitted"
    )
