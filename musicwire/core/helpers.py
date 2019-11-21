from django.conf import settings
from raven import Client


def sentry_logger(message):
    """Sentry configuration"""
    sentry = Client(settings.RAVEN_DSN)
    sentry.tags_context({'Error Message': message})
    sentry.captureException()
