import json
import logging
import uuid
from functools import wraps

from django.conf import settings
from raven import Client
from requests import exceptions as requests_exceptions
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler
from urllib3 import exceptions

from musicwire.provider.datastructures import ClientResult

logger = logging.getLogger(__name__)


def request_validator(func):
    @wraps(func)
    def aux(*args, **kwargs):
        error = False
        error_message = None
        result = None
        try:
            response = func(*args, **kwargs)
        except (exceptions.ReadTimeoutError,
                requests_exceptions.ReadTimeout,
                exceptions.ConnectionError,
                requests_exceptions.ConnectionError) as e:
            logging.error(f"Connection error as {e}")
            return ClientResult(result=result, error=True, error_msg='Connection Error')
        if response and response.ok:
            result = response.json()
        else:
            logger.error(f"Response error: {response.text}")
            error = True
            error_message = response.text
        return ClientResult(result=result, error=error, error_msg=error_message)
    return aux


def custom_exception_handler(exc, context: dict):
    """
    Rest Framework exception handler
    :param exc: AttributeError etc
    :param context: dict
    :return: raise exc
    """
    response = exception_handler(exc, context)
    if not isinstance(exc, APIException):
        raise exc
    elif isinstance(response.data, dict):
        response.data = response.data[next(iter(response.data))]
    error_message = response.data[0]

    code = getattr(exc, 'code', None)
    if code is None:
        code = 'VALIDATION_ERROR'

    if not isinstance(error_message, dict):
        error_message = json.loads(error_message)

    data = {
        'status_code': response.status_code,
        'code': code,
        'error_message': error_message
    }

    return Response(data, status=response.status_code, headers=response._headers)


def sentry_logger(message):
    """Sentry configuration"""
    sentry = Client(settings.RAVEN_DSN)
    sentry.tags_context({'Error Message': message})
    sentry.captureException()


def generate_uniq_id(size=32):
    return uuid.uuid1().hex[:size]
