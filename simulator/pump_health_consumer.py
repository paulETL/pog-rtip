from confluent_kafka import Consumer

from clickhouse_connect import (
    get_client
)

from datetime import datetime

import json
import os


consumer = Consumer({

    'bootstrap.servers':
        'redpanda:9092',

    'group.id':
        'pump-health-group',

    'auto.offset.reset':
        'latest'
})


consumer.subscribe([
    'pump_health'
])


client = get_client(

    host='clickhouse',

    port=8123,

    username=os.getenv(
        'CLICKHOUSE_USER'
    ),

    password=os.getenv(
        'CLICKHOUSE_PASSWORD'
    ),

    database=os.getenv(
        'CLICKHOUSE_DB'
    )
)


print(
    "Pump health consumer started..."
)


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


    if 'timestamp' not in event:
        continue


    row = [[

        datetime.fromisoformat(
            event['timestamp']
        ),

        event['station_id'],

        event['state'],

        event['pump_id'],

        event['temperature'],

        event['pressure'],

        event['vibration'],

        event['uptime_hours'],

        event['failure_flag']
    ]]


    client.insert(

        'fact_pump_health',

        row,

        column_names=[

            'timestamp',

            'station_id',

            'state',

            'pump_id',

            'temperature',

            'pressure',

            'vibration',

            'uptime_hours',

            'failure_flag'
        ]
    )


    print(

        f"Inserted pump telemetry: "

        f"{event['station_id']} | "

        f"{event['pump_id']}"
    )
