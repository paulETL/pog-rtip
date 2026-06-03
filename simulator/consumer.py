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
    'group.id': 'pog-consumer-group',
    'auto.offset.reset': 'latest'
})

consumer.subscribe(['pump_transactions'])

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

print("Transaction consumer started...")

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

    if 'event_time' not in event:
        continue


    event['event_time'] = (
        datetime.fromisoformat(
            event['event_time']
        )
    )

    row = [[
        event['event_id'],
        event['event_time'],

        event['station_id'],
        event['state'],

        event['pump_id'],
        event['attendant_id'],
        event['shift'],

        event['fuel_type'],

        event['requested_liters'],
        event['actual_dispensed_liters'],
        event['variance_liters'],

        event['unit_price'],

        event['expected_amount'],
        event['actual_amount_paid'],

        event['payment_type'],

        event['fraud_flag']
    ]]

    client.insert(
        'fact_transactions',
        row,
        column_names=[

            'event_id',
            'timestamp',

            'station_id',
            'state',

            'pump_id',
            'attendant_id',
            'shift',

            'fuel_type',

            'requested_liters',
            'actual_dispensed_liters',
            'variance_liters',

            'unit_price',

            'expected_amount',
            'actual_amount_paid',

            'payment_type',

            'fraud_flag'
        ]
    )

    print(
        f"Inserted transaction: "
        f"{event['event_id']}"
    )