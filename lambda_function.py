import requests
import xml.etree.ElementTree as ET

XAC_POLLEN_STATIONS = ("barcelona",)


def fetch_and_store_pollen(s3_client):
    """Fetch XAC pollen forecast XML for each station and write to S3.

    The XAC API updates weekly. We key by the week-start date the payload
    reports, so multiple calls within the same week overwrite the same object.
    """
    for station in XAC_POLLEN_STATIONS:
        url = f"https://aerobiologia.cat/api/v0/forecast/{station}/en/xml"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            body = resp.text
            root = ET.fromstring(body)
            start = root.findtext(".//report/date/start") or "unknown"
            key = f"pollen/{station}-week-{start}.xml"
            s3_client.put_object(Body=body, Bucket="air-quality-data-dumps", Key=key)
            print(f"Saved pollen data for {station} to {key}")
        except Exception as e:
            print(f"Failed to fetch pollen for {station}: {e}")


class AirQualityAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.waqi.info/feed"
        self.params = {
            "token": self.api_key
        }

    def make_get_request(self, endpoint, params=None, data=None):
        url = f'{self.base_url}{endpoint}'
        return requests.request(url=url, method='GET', params=params, json=data).json()


    def get_city_data(self, city):
        endpoint = f"/{city}"
        output = self.make_get_request(endpoint=endpoint, params=self.params)
        return output
    

def lambda_handler(event, context):
    import os
    import boto3
    import json

    s3_client = boto3.client('s3')

    api = AirQualityAPI(api_key=os.environ["AQ_API_KEY"])
    cities = ("Barcelona","Madrid","Valencia","Granada","Sevilla","Bilbao","Malaga","Valladolid","Zaragoza","Huelva","Soria","Gijon","Palma")
    
    for city in cities:
        data = api.get_city_data(city=city)
        try:
            timestamp =  data["data"]["time"]["iso"]
            s3_client.put_object(Body=str(data), Bucket="air-quality-data-dumps", Key=f"{city}-{timestamp}.json")
        except Exception as e:
            print(f'Failed for city {city}')
            print(data)

    fetch_and_store_pollen(s3_client)

    print("Done!")
    
    return {
        'statusCode': 200,
        'body': json.dumps(cities)
    }
