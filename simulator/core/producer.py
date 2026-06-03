from confluent_kafka import Producer
from core.tank_generator import generate_tank_readings
from core.pump_health_generator import (
    generate_pump_health
)
from core.delivery_generator import (
    generate_deliveries
)
from datetime import datetime
import json
import random
import uuid
import time

# redpanda
producer = Producer({
    "bootstrap.servers": "redpanda:9092"
})

fuel_prices = {
    "PMS": 1300,
    "AGO": 1800,
    "LPG": 1250,
    "ATK": 1800
}


def demand_multiplier():

    hour = datetime.now().hour

    if 6 <= hour < 9:
        return 2.2

    elif 16 <= hour < 20:
        return 2.8

    elif 22 <= hour or hour < 5:
        return 0.4

    return 1.0


def load_stations():

    with open("config/stations.json", "r") as f:
        return json.load(f)


def initialize_inventory(stations):

    inventory = {}

    for station in stations:

        inventory[station["station_id"]] = {}

        for fuel, capacity in station["tank_capacity"].items():

            starting_volume = round(
                capacity * random.uniform(0.45, 0.95),
                2
            )

            inventory[station["station_id"]][fuel] = starting_volume

    return inventory


def generate_event(stations, inventory):

    station = random.choice(stations)

    station_id = station["station_id"]

    fuel_type = random.choice(list(fuel_prices.keys()))

    available = inventory[station_id][fuel_type]

    if available <= 100:
        return None

    multiplier = demand_multiplier()

    requested_liters = round(
        random.uniform(5, 80) * multiplier,
        2
    )
    # FRAUD PROBABILITY

    fraud_probability = station.get(
        "fraud_probability",
        0.15
    )


    fraud_triggered = (
        random.random() < fraud_probability
    )

    if fraud_triggered:

        fraud_delta = round(
            random.uniform(0.05, 0.30),
            2
        )

        actual_dispensed_liters = round(
            requested_liters - fraud_delta,
            2
        )

    else:

        actual_dispensed_liters = requested_liters

    inventory[station_id][fuel_type] -= (
        actual_dispensed_liters
    )

    unit_price = fuel_prices[fuel_type]

    expected_amount = round(
        requested_liters * unit_price,
        2
    )

    actual_amount_paid = expected_amount

    event = {
        "event_id": str(uuid.uuid4()),
        "event_time": datetime.now().isoformat(),
        "station_id": station_id,
        "state": station["state"],
        "pump_id": (
            f"pump_{random.randint(1, station['pump_count'])}"
        ),
        "attendant_id": (
            f"att_{random.randint(1,15)}"
        ),
        "shift": random.choice([
            "morning",
            "afternoon",
            "night"
        ]),
        "fuel_type": fuel_type,
        "requested_liters": requested_liters,
        "actual_dispensed_liters": (
            actual_dispensed_liters
        ),
        "variance_liters": round(
            actual_dispensed_liters -
            requested_liters,
            2
        ),
        "unit_price": unit_price,
        "expected_amount": expected_amount,
        "actual_amount_paid": (
            actual_amount_paid
        ),
        "payment_type": random.choice([
            "cash",
            "card",
            "transfer"
        ]),
        "fraud_flag": fraud_triggered
    }

    producer.produce(
        "pump_transactions",
        json.dumps(event).encode("utf-8")
    )

    producer.flush()

    return event


def run():

    stations = load_stations()

    inventory = initialize_inventory(stations)

    print(f"Loaded {len(stations)} stations")

    while True:

        generate_tank_readings(
            stations,
            inventory
        )

        generate_pump_health(stations)

        generate_deliveries(
            stations,
            inventory
        )

        event = generate_event(
            stations,
            inventory
        )

        if event:
            print(event)

        time.sleep(2)


if __name__ == "__main__":
    run()