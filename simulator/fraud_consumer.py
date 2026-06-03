from confluent_kafka import Consumer
from clickhouse_connect import get_client

from datetime import datetime

import json
import os


consumer = Consumer({

    'bootstrap.servers': 'redpanda:9092',

    'group.id': 'fraud-consumer-group',

    'auto.offset.reset': 'earliest'
})


consumer.subscribe([
    'pump_transactions'
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


print("Fraud consumer started...")


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


    variance = event[
        'variance_liters'
    ]


    if variance < -0.05:

        fraud_score = round(
            abs(variance) * 100,
            2
        )


        row = [[

            datetime.fromisoformat(
                event['event_time']
            ),

            event['station_id'],

            event['state'],

            event['attendant_id'],

            event['pump_id'],

            event['fuel_type'],

            event['requested_liters'],

            event['actual_dispensed_liters'],

            variance,

            event['expected_amount'],

            event['actual_amount_paid'],

            fraud_score,

            'UNDER_DISPENSING'
        ]]


        client.insert(

            'fraud_transactions',

            row,

            column_names=[

                'timestamp',

                'station_id',

                'state',

                'attendant_id',

                'pump_id',

                'fuel_type',

                'requested_liters',

                'actual_dispensed_liters',

                'variance_liters',

                'expected_amount',

                'actual_amount_paid',

                'fraud_score',

                'fraud_reason'
            ]
        )


        print(

            f"FRAUD DETECTED | "

            f"{event['station_id']} | "

            f"{event['pump_id']} | "

            f"{variance}"
        )
