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
        try:
            response = func(*args, **kwargs)
        except (exceptions.ReadTimeoutError,
                requests_exceptions.ReadTimeout,
                exceptions.ConnectionError,
                requests_exceptions.ConnectionError) as e:
            logging.error(f"Connection error as {e}")
            return
        if response and response.ok:
            response_data = response.json()
        else:
            logger.error(f"Response error: {response.text}")
            return
        return response_data
    return aux


def sentry_logger(message):
    """Sentry configuration"""
    sentry = Client(settings.RAVEN_DSN)
    sentry.tags_context({'Error Message': message})
    sentry.captureException()
