import requests
import random
from requests.auth import HTTPBasicAuth
import os
import sys
import json
import datetime

import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

class BlastApi():
    def __init__(self, conf):
        self.conf = conf
        self.conf['api_url_base'] = f'''{self.conf['api_url_protocol']}://{self.conf['api_url_authority']}'''
        if self.conf['api_url_basepath']:
            self.conf['api_url_base'] += f'''/{self.conf['api_url_basepath']}'''
        logger.debug(self.conf)
        # if self.conf['token']:
        #     self.api_token = self.conf['token']
        # else:
        #     # import base64
        #     # basic_auth_credentials = base64.b64encode(bytes(f'''{self.conf['username']}:{self.conf['password']}''', 'utf-8'))
        #     self.api_token = self.obtain_api_token(username=self.conf['username'], password=self.conf['password'])
        self.json_headers = {
            # 'Authorization': f'''Token {self.api_token}''',
            'Content-Type': 'application/json',
        }
    def display_response(self, response, parse_json=True):
        try:
            assert isinstance(response, requests.Response)
            # assert response.text
            # assert response.status_code
        except:
            logger.debug(f'''Invalid response object''')
            return
        logger.debug(f'''Response code: {response.status_code}''')
        try:
            assert response.status_code in range(200,300)
            if parse_json:
                data = response.json()
                logger.debug(json.dumps(data, indent=2))
                return data
            else:
                return response
        except:
            try:
                logger.debug(f'''ERROR: {json.dumps(response.text, indent=2)}''')
            except:
                logger.debug(f'''ERROR: {response.text}''')

    def obtain_api_token(self, username, password):
        response = requests.post(
            # This URL must NOT have a trailing slash
            f'''{self.conf['api_url_base']}/token''',
            json={
                'username': username,
                'password': password,
            },
            headers={
                'Content-Type': 'application/json',
            },
            auth=HTTPBasicAuth(self.conf['username'], self.conf['password']),
        )
        data = self.display_response(response)
        return data['token']

    def launch_workflow(self, name=f'''transient{random.randrange(10000,99999)}'''):
        response = requests.put(
            # The URL trailing slash is required without setting APPEND_SLASH=False
            f'''{self.conf['api_url_base']}/workflow/{name}''',
            headers=self.json_headers,
            # auth=self.basic_auth,
        )
        return self.display_response(response)

if __name__ == "__main__":
    import sys
    import time

    # Import credentials and config from environment variables
    api = BlastApi({
        'username': os.environ.get('CE_USERNAME', 'admin'),
        'password': os.environ.get('CE_PASSWORD', ''),
        'token': os.environ.get('CE_API_TOKEN', ''),
        'api_url_protocol': os.environ.get('CE_API_URL_PROTOCOL', 'http'),
        'api_url_authority': os.environ.get('CE_API_URL_AUTHORITY', 'localhost:8000'),
        'api_url_basepath': os.environ.get('CE_API_URL_BASEPATH', 'api'),
    })

    transient_name = sys.argv[1]

    api.launch_workflow(name=transient_name)
    sys.exit()
