import requests

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
    

if __name__ == "__main__":
    from credentials import AQ_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    import boto3

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    b = s3_client.list_buckets()

    api = AirQualityAPI(api_key=AQ_API_KEY)
    cities = ("Barcelona","Madrid","Valencia","Granada","Sevilla","Bilbao","Malaga","Valladolid","Zaragoza","Huelva","Soria","Gijon","Palma")

    for city in cities:
        data = api.get_city_data(city=city)
        try:
            timestamp =  data["data"]["time"]["iso"]
        except Exception as e:
            print(data)
            raise e
        s3_client.put_object(Body=str(data), Bucket="air-quality-data-dumps", Key=f"{city}-{timestamp}.json")
    print("Done!")