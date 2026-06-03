from confluent_kafka import Producer

from datetime import datetime

import random
import uuid
import json

# redpanda
producer = Producer({
    "bootstrap.servers":
        "redpanda:9092"
})


suppliers = [
    "NNPCL",
    "MRS",
    "Rainoil",
    "TotalEnergies",
    "Ardova"
]


def generate_deliveries(
    stations,
    inventory
):

    for station in stations:

        station_id = (
            station["station_id"]
        )

        for fuel_type, capacity in (
            station["tank_capacity"].items()
        ):

            current_volume = inventory[
                station_id
            ][fuel_type]


            utilization = (
                current_volume / capacity
            )

            # DELIVERY TRIGGER


            if utilization < 0.35:

                delivered_volume = round(
                    random.uniform(
                        5000,
                        20000
                    ),
                    2
                )


                inventory[
                    station_id
                ][fuel_type] += (
                    delivered_volume
                )


                if inventory[
                    station_id
                ][fuel_type] > capacity:

                    inventory[
                        station_id
                    ][fuel_type] = (
                        capacity
                    )


                event = {

                    "delivery_id":
                        str(uuid.uuid4()),

                    "timestamp":
                        datetime.now().isoformat(),

                    "station_id":
                        station_id,

                    "state":
                        station["state"],

                    "fuel_type":
                        fuel_type,

                    "supplier":
                        random.choice(
                            suppliers
                        ),

                    "delivered_volume":
                        delivered_volume,

                    "tank_capacity":
                        capacity,

                    "post_delivery_volume":
                        inventory[
                            station_id
                        ][fuel_type],

                    "tanker_plate":
                        f"ABC-{random.randint(100,999)}XY"
                }


                producer.produce(

                    "fuel_deliveries",

                    json.dumps(event).encode(
                        "utf-8"
                    )
                )

    producer.flush()

    print(
        "Fuel delivery events emitted"
    )
