# Download and ingest transients from the Transient Name Server (TNS)
import os
from collections import OrderedDict
import json
import requests
import time
from .models import Transient
from .decorators import log_resource_call

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

@log_resource_call(resource_name='Transient name server')
def query_tns(data, headers, search_url):
    """
    Query the TNS server
    """
    response = requests.post(search_url, headers=headers, data=data)
    response = json.loads(response.text)

    reponse_message = response.get('id_message')
    response_id_code = response.get('id_code')

    response_status_good = response_id_code == 200
    data = response.get('data', {}).get('reply') if response_status_good else []
    response_reset_time = response.get('data', {}).get('total', {}).get('reset')

    response_return = {'response_message': reponse_message, 'response_id_code':
                        response_id_code, 'data': data,
                       'response_reset_time':  response_reset_time}
    return response_return


def rate_limit_query_tns(data, headers, search_url):
    """
    Query TNS but wait if we have reached too many api requests.
    """
    response = query_tns(data, headers, search_url)
    too_many_requests = response['response_id_code'] == 429
    while too_many_requests:
        time_util_rest = response['response_reset_time']
        time.sleep(time_util_rest + 1)
        response = query_tns(data, headers, search_url)
        too_many_requests = response['response_id_code'] != 429
    return response['data']


def get_transients_from_tns(time_after, sandbox=False, tns_credentials=None):
    """
    Gets transient data from TNS for all transients with public
    timestamp after time_after.

    Args:
        time_after (datetime.datetime):  Time to search the transient name
            server for new transients.
        sandbox (bool): If true uses the transient name server sandbox API,
            else uses the live transisent name server API
        tns_credentials (dict): Transient name server credentials, need to have
            the keys, TNS_BOT_ID, TNS_BOT_NAME, and TNS_BOT_API_KEY.
    Returns:
        (list): List of Transients retrieved transients from the transient name
            server.
    """

    tns_bot_id = tns_credentials['TNS_BOT_ID']
    tns_bot_name = tns_credentials['TNS_BOT_NAME']
    tns_bot_api_key = tns_credentials['TNS_BOT_API_KEY']

    headers = build_tns_header(tns_bot_id, tns_bot_name)

    entry = 'sandbox' if sandbox else 'www'
    tns_api_url = f'https://{entry}.wis-tns.org/api/get'

    search_tns_url = build_tns_url(tns_api_url, mode='search')
    get_tns_url = build_tns_url(tns_api_url, mode='get')

    search_data = build_tns_search_query_data(tns_bot_api_key, time_after)
    transients = rate_limit_query_tns(search_data, headers, search_tns_url)

    blast_transients = []

    for transient in transients:
        get_data = build_tns_get_query_data(tns_bot_api_key, transient)
        tns_transient = rate_limit_query_tns(get_data, headers, get_tns_url)
        blast_transient = tns_to_blast_transient(tns_transient)
        blast_transients.append(blast_transient)

    return blast_transients


def tns_to_blast_transient(tns_transient):
    """Convert transient name server transient into blast transient data model.

    Args:
        tns_transient (Dict): Dictionary containing transient name server
            transient information.
    Returns:
        blast_transient (Transient): Transient object with the
            tns_transient data.
    """
    blast_transient = Transient(tns_name=tns_transient['objname'],
                                tns_id=tns_transient['objid'],
                                ra_deg=tns_transient['radeg'],
                                dec_deg=tns_transient['decdeg'],
                                tns_prefix=tns_transient['name_prefix'],
                                public_timestamp=tns_transient['discoverydate'])
    return blast_transient


def build_tns_header(tns_bot_id, tns_bot_name):
    """
    Builds the TNS header dictionary.

    Args:
        tns_bot_id (int): Transient name server bot id.
        tns_bot_name (str): Transient name server bot name.
    Returns:
        (dict): Transient name server header dictionary.
    """
    tns_marker = (f'tns_marker{{\"tns_id\": {int(tns_bot_id)},'
                  f'\"type\": \"bot\", \"name\": \"{tns_bot_name}\"}}')
    return {'User-Agent': tns_marker}


def build_tns_query_data(tns_bot_api_key, data_obj):
    """
    Builds tns search data dictionary.

    Args:
        tns_bot_api_key (str): Transient name server bot api key.
        data_obj (list): List of data representing the tns query.
    Returns:
        (dict): Transient name server query data.

    """
    data_obj = OrderedDict(data_obj)
    return {'api_key': tns_bot_api_key,
            'data': json.dumps(data_obj)}


def build_tns_url(tns_api_url, mode=None):
    """
    Builds the url to the tns api service

    Args:
        tns_api_url (str): URL of the Transient name server API.
        mode (str): Which endpoint to access the API. Options are search and get
    Returns:
        (str) Full transient name server api url
    """
    if mode == 'search':
        url_end_point = '/Search'
    elif mode == 'get':
        url_end_point = '/object'
    else:
        raise ValueError('Mode invalid, provide a valid mode (search or get)')
    return tns_api_url + url_end_point


def build_tns_get_query_data(tns_bot_api_key, transient):
    """
    Build the the get query data for a TNS transient.

    Args:
        tns_bot_api_key (str): Transient name server bot api key.
        transient (dict): Transient name server transient information.
    Returns:
        (dict): Transient name server query data.

    """
    get_obj = [("objname", transient['objname']),
               ("objid", transient['objid']),
               ("photometry", "0"),
               ("spectra", "0")]
    return build_tns_query_data(tns_bot_api_key, get_obj)


def build_tns_search_query_data(tns_bot_api_key, time_after):
    """
    Build the the search query to find tns transients with a public timestamp
    after time after.

    Args:
        tns_bot_api_key (str): Transient name server bot api key.
        time_after (datetime.datetime): Time to search the transient name
            server for new transients.
    Returns:
        (dict): Transient name server query data.

    """
    search_obj = [("public_timestamp", time_after.isoformat())]
    return build_tns_query_data(tns_bot_api_key, search_obj)