import csv
from urllib.request import urlopen
import json

input_csv_file_path = ''
api_endpoint = response = '/api/transient/post/'

with open(input_csv_file_path, newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for transient in reader:
        ra, dec = transient['ra'], transient['dec']
        post_url = f"{api_endpoint}name={transient['name']}&ra={ra}&dec={dec}"
        response = urlopen(post_url)
        data = json.loads(response.read())
        post_message = data.content.get("message", "no message returned by blast")
        post_status = f"HTTP status: {data.status_message}"
        print(f"{post_status} | {post_message}")







