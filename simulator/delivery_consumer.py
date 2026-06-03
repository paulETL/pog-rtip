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
        'delivery-consumer-group-v2',

    'auto.offset.reset':
        'earliest'
})


consumer.subscribe([
    'fuel_deliveries'
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
    "Fuel delivery consumer started..."
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
    print(event)


    if 'timestamp' not in event:
        continue


    row = [[

        datetime.fromisoformat(
            event['timestamp']
        ),

        event['delivery_id'],

        event['station_id'],

        event['state'],

        event['fuel_type'],

        event['supplier'],

        event['delivered_volume'],

        event['tank_capacity'],

        event[
            'post_delivery_volume'
        ],

        event['tanker_plate']
    ]]

    print("Attempting insert...")
    print(row)

    try:

        client.insert(

            'fact_fuel_deliveries',

            row,

            column_names=[

                'timestamp',

                'delivery_id',

                'station_id',

                'state',

                'fuel_type',

                'supplier',

                'delivered_volume',

                'tank_capacity',

                'post_delivery_volume',

                'tanker_plate'
            ]
        )

        print("Insert success")

        print(

            f"Fuel delivery inserted: "

            f"{event['station_id']} | "

            f"{event['fuel_type']}"
        )

    except Exception as e:

        print("Insert failed")
        print(e)




    print(

        f"Fuel delivery inserted: "

        f"{event['station_id']} | "

        f"{event['fuel_type']}"
    )
