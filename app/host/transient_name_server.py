# Download and ingest transients from the Transient Name Server (TNS)
import os
from collections import OrderedDict
import json
import requests
from datetime import date

def get_tns_credentials():
    """
    Retrieves TNS credentials from environment variables
    """
    credentials = ['TNS_BOT_API_KEY', 'TNS_BOT_NAME', 'TNS_USERNAME',
                   'TNS_BOT_ID']

    for credential in credentials:
        credential_value = os.environ.get(credential)
        if credential_value is None:
            raise ValueError(f'{credential} not defined in environment')

    return {credential: os.environ[credential] for credential in credentials}

def search_tns(time_after, tns_config):
    """
    Queries TNS for transients with public timestamp > time_after.
    """
    search_obj = [("ra", ""), ("dec", ""), ("radius", ""), ("units", ""),
                  ("objname", ""), ("internal_name", ""),
                  ("public_timestamp", time_after.isoformat())]
    search_url = tns_config['tns_api_url'] + "/search"
    headers = {'User-Agent': tns_config['tns_marker']}
    json_file = OrderedDict(search_obj)
    search_data = {'api_key': tns_config['tns_bot_api_key'],
                   'data': json.dumps(json_file)}
    return requests.post(search_url, headers=headers, data=search_data)

def ingest_new_transients(sandbox=False):
    """
    Ingest new transients from the transient name server
    """
    bot = get_tns_credentials()
    TNS_BOT_ID, TNS_BOT_NAME = bot['TNS_BOT_ID'], bot['TNS_BOT_NAME']
    TNS_BOT_API_KEY = bot['TNS_BOT_API_KEY']

    if sandbox:
        tns_api_url = 'https://sandbox.wis-tns.org/api/get'
    else:
        tns_api_url = 'https://www.wis-tns.org/api/get'

    tns_marker = (f'tns_marker{{\"tns_id\": {TNS_BOT_ID},'
                  f'\"type\": \"bot\", \"name\": \"{TNS_BOT_NAME}\"}}')

    config = {'tns_marker': tns_marker, 'tns_bot_api_key': TNS_BOT_API_KEY,
              'tns_api_url': tns_api_url}
    search_results = search_tns(date(2022, 1, 1), config)

    print(type(search_results.text))

    return None

ingest_new_transients()