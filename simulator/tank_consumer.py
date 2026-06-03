from confluent_kafka import Consumer
from clickhouse_connect import get_client
from datetime import datetime
import os
import json

consumer = Consumer({
    'bootstrap.servers': os.getenv(
        'KAFKA_BROKER',
        'redpanda:9092'
    ),
    'group.id': 'tank-consumer-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['tank_readings'])

client = get_client(
    host=os.getenv(
        'CLICKHOUSE_HOST',
        'clickhouse'
    ),
    port=int(
        os.getenv(
            'CLICKHOUSE_PORT',
            8123
        )
    ),
    username=os.getenv(
        'CLICKHOUSE_USER',
        'admin'
    ),
    password=os.getenv(
        'CLICKHOUSE_PASSWORD',
        'admin123'
    ),
    database=os.getenv(
        'CLICKHOUSE_DB',
        'pog'
    )
)

print("Tank consumer started...")


while True:

    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        print(msg.error())
        continue

    event = json.loads(
        msg.value().decode('utf-8')
    )

    event['timestamp'] = (
        datetime.fromisoformat(
            event['timestamp']
        )
    )

    row = [[
        event['timestamp'],
        event['station_id'],
        event['state'],
        event['fuel_type'],
        event['current_volume'],
        event['tank_capacity'],
        event['utilization_pct']
    ]]

    client.insert(
        'fact_tank_readings',
        row,
        column_names=[
            'timestamp',
            'station_id',
            'state',
            'fuel_type',
            'current_volume',
            'tank_capacity',
            'utilization_pct'
        ]
    )

    print(
        f"Inserted tank telemetry: "
        f"{event['station_id']}"
    )