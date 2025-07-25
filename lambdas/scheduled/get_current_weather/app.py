import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import boto3
import requests


def get_secret(secret_name):
    client = boto3.client(
        "secretsmanager",
        region_name="ap-northeast-1",
    )
    response = client.get_secret_value(SecretId=secret_name)
    secret_dict = json.loads(response["SecretString"])
    return secret_dict


def save_to_s3(bucket_name, key, data):
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data),
    )


def lambda_handler(event, context):
    environment = os.environ["ENVIRONMENT_NAME"]

    # APIキー取得
    secret_name = f"weather-app/{environment}/api-key"
    secrets = get_secret(secret_name)
    api_key = secrets["OPENWEATHER_API_KEY"]

    CITIES = [
        {"name": "Sapporo", "lat": 43.0621, "lon": 141.3544},
        {"name": "Tokyo", "lat": 35.6812, "lon": 139.7671},
        {"name": "Kanazawa", "lat": 36.5613, "lon": 136.6562},
        {"name": "Kochi", "lat": 33.5597, "lon": 133.5311},
        {"name": "Naha", "lat": 26.2124, "lon": 127.6809},
    ]
    bucket_name = f"weather-data-ak0407-{environment}"
    today = datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat()

    for city in CITIES:
        try:
            # 気象データ取得
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": city["lat"],
                    "lon": city["lon"],
                    "appid": api_key,
                    "units": "metric",
                },
            )
            response.raise_for_status()

            response_dict = response.json()
            unix = response_dict["dt"]
            key = f"weather-data/{city['name']}/{today}/{unix}.json"
            save_to_s3(bucket_name, key, response_dict)
            print(f"Saved data for {city['name']} to {key}")

        except Exception as e:
            print(f"Failed to fetch or store data for {city['name']}: {e}")
