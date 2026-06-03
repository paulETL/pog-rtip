from confluent_kafka import Producer
from datetime import datetime
import json
import time

# redpanda
producer = Producer({
    "bootstrap.servers": "redpanda:9092"
})


def generate_tank_readings(stations, inventory):

    for station in stations:

        station_id = station["station_id"]

        for fuel_type, current_volume in inventory[station_id].items():

            capacity = station["tank_capacity"][fuel_type]

            utilization_pct = round(
                (current_volume / capacity) * 100,
                2
            )

            event = {

                "timestamp": datetime.now().isoformat(),

                "station_id": station_id,

                "state": station["state"],

                "fuel_type": fuel_type,

                "current_volume": round(current_volume, 2),

                "tank_capacity": capacity,

                "utilization_pct": utilization_pct
            }

            producer.produce(
                "tank_readings",
                json.dumps(event).encode("utf-8")
            )

    producer.flush()

    print("Tank telemetry emitted")

    time.sleep(10)