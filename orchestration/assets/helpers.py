import json
from io import BytesIO

import pandas as pd


def read_json_from_minio(minio_client, bucket, object_name):
    response = minio_client.get_object(bucket, object_name)

    data = json.loads(response.read().decode("utf-8"))

    if isinstance(data, list):
        return pd.DataFrame(data)

    return pd.DataFrame([data])

