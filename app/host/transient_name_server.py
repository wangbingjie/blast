# Download and ingest transients from the Transient Name Server (TNS)
import os
from collections import OrderedDict
import json
import requests
from datetime import date
import time
from host.models import Transient

def get_tns_credentials():
    """
    Retrieves TNS credentials from environment variables
    """
    credentials = ['TNS_BOT_API_KEY', 'TNS_BOT_NAME',
                   'TNS_BOT_ID']

    for credential in credentials:
        credential_value = os.environ.get(credential)
        if credential_value is None:
            raise ValueError(f'{credential} not defined in environment')

    return {credential: os.environ[credential] for credential in credentials}

def query_tns_api(url_endpoint, data_obj, tns_config):
    """
    Query TNS API
    """
    headers = {'User-Agent': tns_config['tns_marker']}
    json_file = OrderedDict(data_obj)
    search_data = {'api_key': tns_config['tns_bot_api_key'],
                   'data': json.dumps(json_file)}
    search_url = tns_config['tns_api_url'] + url_endpoint
    response = requests.post(search_url, headers=headers, data=search_data)
    response = json.loads(response.text)
    print(search_data)
    # if we've made too many requests to the api wait and then try again
    if response['id_code'] == 429:
        time_util_rest = int(response['data']['total']['reset'])
        time.sleep(time_util_rest + 1)
        response = requests.post(search_url, headers=headers, data=search_data)
        response = json.loads(response.text)

    if response['id_code'] == 200:
        response_data = response['data']['reply']
    else:
        response_data = None
    return response_data

def get_transients_from_tns(time_after, tns_config):
    """
    Gets transient data from TNS for all transients with public
    timestamp > time_after.
    """
    search_obj = [("public_timestamp", time_after.isoformat())]
    transients = query_tns_api('/Search', search_obj, tns_config)

    blast_transients = []
    for transient in transients:
        get_obj = [("objname", transient['objname']),
                   ("objid", transient['objid']),
                   ("photometry", "0"),
                   ("spectra", "0")]
        tns_data = query_tns_api('/object', get_obj, tns_config)
        blast_transients.append(tns_to_blast_transient(tns_data))

    return blast_transients


def tns_to_blast_transient(tns_transient):
    """Convert TNS transient into blast transient data model"""
    blast_transient = Transient(tns_name=tns_transient['objname'],
                                tns_id=tns_transient['objid'],
                                ra_deg= tns_transient['radeg'],
                                dec_deg=tns_transient['decdeg'],
                                tns_prefix=tns_transient['name_prefix'])
    return blast_transient


def ingest_new_transients(date_after, sandbox=False):
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
    transients = get_transients_from_tns(date_after, config)

    for transient in transients: transient.save()

    return None

import datetime
time = datetime.datetime.now() - datetime.timedelta(hours=3)
ingest_new_transients(time)