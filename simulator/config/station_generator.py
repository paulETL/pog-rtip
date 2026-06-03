import json
import random

from states import (
    states_distribution,
    STATE_COORDINATES
)

stations = []

for state, count in states_distribution.items():

    for i in range(1, count + 1):

        center_lat, center_lon = (
            STATE_COORDINATES[state]
        )

        latitude = round(
            center_lat +
            random.uniform(-0.12, 0.12),
            6
        )

        longitude = round(
            center_lon +
            random.uniform(-0.12, 0.12),
            6
        )

        station = {

            "station_id":
                f"{state.lower().replace(' ', '_')}_{str(i).zfill(3)}",

            "state": state,

            "latitude": latitude,

            "longitude": longitude,

            "pump_count":
                random.randint(5, 8),

            "fraud_risk":
                round(random.uniform(0.05, 0.4), 2),

            "tank_capacity": {

                "PMS":
                    random.randint(30000, 50000),

                "AGO":
                    random.randint(10000, 25000),

                "LPG":
                    random.randint(5000, 15000),

                "ATK":
                    random.randint(8000, 20000)
            }
        }

        stations.append(station)

with open("stations.json", "w") as f:

    json.dump(
        stations,
        f,
        indent=2
    )

print(
    f"Generated {len(stations)} stations"
)
