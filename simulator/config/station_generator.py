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

            "station_age":
                random.randint(1, 15),


            "fraud_risk": {

                "Rivers": round(random.uniform(0.06, 0.09), 2),
                "Delta": round(random.uniform(0.06, 0.08), 2),
                "Akwa Ibom": round(random.uniform(0.05, 0.08), 2),

                "Lagos": round(random.uniform(0.02, 0.05), 2),
                "FCT": round(random.uniform(0.01, 0.04), 2),

                "Anambra": round(random.uniform(0.04, 0.07), 2),
                "Imo": round(random.uniform(0.04, 0.07), 2),
                "Enugu": round(random.uniform(0.03, 0.06), 2),

                "Edo": round(random.uniform(0.03, 0.06), 2),
                "Cross River": round(random.uniform(0.04, 0.07), 2),

                "Ogun": round(random.uniform(0.02, 0.05), 2),
                "Oyo": round(random.uniform(0.02, 0.05), 2),
                "Ondo": round(random.uniform(0.02, 0.05), 2),

                "Kano": round(random.uniform(0.01, 0.04), 2),
                "Kaduna": round(random.uniform(0.01, 0.04), 2),
                "Plateau": round(random.uniform(0.01, 0.04), 2),
                "Benue": round(random.uniform(0.02, 0.05), 2),
                "Kwara": round(random.uniform(0.01, 0.04), 2),
                "Borno": round(random.uniform(0.01, 0.03), 2),

                "Abia": round(random.uniform(0.03, 0.06), 2)

            }[state],



            "station_tier":
                random.choices(
                    ["mega", "urban", "standard", "rural"],
                    weights=[10, 25, 45, 20],
                    k=1
                )[0],

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
