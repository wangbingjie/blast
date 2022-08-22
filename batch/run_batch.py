import csv
from urllib.request import urlopen
import json

input_csv_file_path = ''
api_endpoint = response = '/api/transient/post/'


def post_transient_from_csv(path_to_input_csv: str, base_url: str) -> None:
    """
    Post transients from csv file to blast for processing.

    Parameters
        path_to_input_csv (str): path to input transient csv file.
        base_url (str): base url to the api
    returns
        None, prints the status of each posted transient
    """
    with open(path_to_input_csv, newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for transient in reader:
        ra, dec = transient['ra'], transient['dec']
        post_url = f"{base_url}name={transient['name']}&ra={ra}&dec={dec}"
        response = urlopen(post_url)
        data = json.loads(response.read())
        post_message = data.content.get("message", "no message returned by blast")
        post_status = f"HTTP status: {data.status_message}"
        print(f"{post_status} | {post_message}")

def download_data_snapshot(path_to_input_csv: str, path_to_output_csv: str, base_url: str) -> None:
    """
    Downloads snapshot of data for transients

    Parameters
        path_to_input_csv (str): path to input transient csv file.
        base_url (str): base url to the api
    Returns
        None
    """
    payloads = []
    with open(path_to_input_csv, newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for transient in reader:
        transient_name = transient['name']
        post_url = f"{base_url}{transient_name}?format=json"
        response = urlopen(post_url)
        data = json.loads(response.read())
        post_message = data.content.get("message", "no message returned by blast")
        post_status = f"HTTP status: {data.status_message}"
        print(f"{post_status} | {post_message}")
        payloads.append(data.content)

    with open(path_to_output_csv, 'w', newline='') as csv_file:
        fieldnames = payloads[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for payload in payloads:
            writer.writerow(payload)

def transient_processing_completed(path_to_output_csv: str) -> bool:
    """
    Checks if a batch of transients have had their processing completed.

    Parameters
        path_to_output_csv (str): Path to output csv file.
    Returns:
        processed_statis (bool): True if all transients have been processed or blocked,
            false otherwise.
    """
    processed_status = True
    with open(path_to_output_csv, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for transient in reader:
            status = transient['transient_processing_status']
            if status == "processing":
                processed_status = False
                break
    return processed_status











