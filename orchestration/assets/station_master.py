import json

from dagster import asset

from assets.databricks_loader import execute_insert


@asset(required_resource_keys={"minio", "databricks"})
def station_master(context):

    minio = context.resources.minio
    conn = context.resources.databricks

    response = minio.get_object(
        "pog-rtip-raw",
        "station_master/stations.json",
    )

    stations = json.loads(
        response.read().decode("utf-8")
    )

    cursor = conn.cursor()

    station_rows = []
    capacity_rows = []

    for row in stations:

        station_rows.append(
            {
                "station_id": row["station_id"],
                "state": row["state"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "pump_count": row["pump_count"],
                "fraud_risk": row["fraud_risk"],
            }
        )

        for fuel_type, capacity in row["tank_capacity"].items():

            capacity_rows.append(
                {
                    "station_id": row["station_id"],
                    "fuel_type": fuel_type,
                    "tank_capacity": capacity,
                }
            )

    execute_insert(
        cursor,
        "workspace.pog_rtip_bronze.raw_station_master",
        station_rows,
    )

    execute_insert(
        cursor,
        "workspace.pog_rtip_bronze.raw_station_tank_capacity",
        capacity_rows,
    )

    conn.commit()

    context.log.info(
        f"Loaded {len(station_rows)} stations and {len(capacity_rows)} tank capacity records"
    )
