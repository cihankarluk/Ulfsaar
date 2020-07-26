import json
import urllib.parse

from abc import abstractmethod

import requests

from musicwire.core.helpers import request_validator
from musicwire.provider.datastructures import ClientResult


class BaseClient:
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs['base_url']

    @abstractmethod
    def get_headers(self):
        raise NotImplemented()

    @request_validator  # type: ClientResult
    def make_request(self, end_point, params=None, data=None, method='GET'):
        headers = self.get_headers()
        url = urllib.parse.urljoin(self.base_url, end_point)
        if data:
            data = json.dumps(dict([(k, v) for k, v in data.items() if v]))

        request = requests.request(
            method,
            url=url,
            headers=headers,
            params=params,
            data=data
        )

        return request
