import json


def read_minio_json(minio_client, bucket, object_name):

    response = minio_client.get_object(
        bucket,
        object_name
    )

    return json.loads(
        response.read().decode("utf-8")
    )

