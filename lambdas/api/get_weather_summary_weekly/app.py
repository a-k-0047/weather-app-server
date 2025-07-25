import os

import boto3
from weather_common.response_utils import api_response
from weather_common.s3_utils import fetch_s3_json

s3 = boto3.client("s3")


def lambda_handler(event, context):
    environment = os.environ["ENVIRONMENT_NAME"]
    bucket_name = f"weather-data-ak0407-{environment}"

    # クエリパラメータ
    params = event.get("queryStringParameters") or {}
    date = params.get("date")
    if not date:
        return api_response(400, {"error": "Missing 'date' query parameter"})

    key = f"analysis-results/summary/weekly/{date}.json"
    body = fetch_s3_json(bucket_name, key, default="[]")

    return api_response(200, body, already_json=True)
