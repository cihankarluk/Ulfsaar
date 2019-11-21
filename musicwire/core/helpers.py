import json

from django.conf import settings
from raven import Client
import logging
from functools import wraps
from urllib3 import exceptions
from requests import exceptions as requests_exceptions

logger = logging.getLogger(__name__)


def request_validator(func):
    @wraps(func)
    def aux(*args, **kwargs):
        response_data = None
        try:
            response = func(*args, **kwargs)
        except (exceptions.ReadTimeoutError,
                requests_exceptions.ReadTimeout,
                exceptions.ConnectionError,
                requests_exceptions.ConnectionError) as e:
            logging.error(f"Connection error as {e}")
            return
        if response:
            try:
                response_data = response.json()
            except (json.decoder.JSONDecodeError, AttributeError) as e:
                logger.error(f"Error while converting json as error: {e}")
                return
        return response_data
    return aux


def sentry_logger(message):
    """Sentry configuration"""
    sentry = Client(settings.RAVEN_DSN)
    sentry.tags_context({'Error Message': message})
    sentry.captureException()
