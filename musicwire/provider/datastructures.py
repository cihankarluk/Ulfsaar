from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientResult:
    result: Optional[dict]
    error: bool
    error_msg: Optional[str]


class ProviderClientError(Exception):
    def __init__(self, http_status, detail):
        super(Exception, self).__init__(detail)
        self.http_status = http_status
