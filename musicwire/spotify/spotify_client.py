import urllib.parse

import requests

from musicwire.core.helpers import request_validator


class Client:
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs['base_url']
        self.token = kwargs['token']

    @request_validator
    def make_request(self, end_point=None, method='GET'):
        token = self.token
        url = urllib.parse.urljoin(self.base_url, end_point)
        params = {'limit': 50}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        return requests.request(method, url=url, headers=headers, params=params)
