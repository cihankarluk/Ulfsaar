"""
Django settings for musicwire project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

APP_ENV = os.getenv("APP_STATE")
logging.warning(f"Using {APP_ENV} environment.")

ALLOWED_HOSTS = [os.getenv("ALLOWED_HOSTS")]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG_STATES = ("TEST", "DEV")
DEBUG = APP_ENV in DEBUG_STATES

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'raven.contrib.django.raven_compat',
    'elasticapm.contrib.django',
    'rest_framework',

    'musicwire.spotify',
    'musicwire.core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'elasticapm.contrib.django.middleware.TracingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR)],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

RAVEN_CONFIG = {
    'dns': os.getenv("RAVEN_DNS")
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'log_to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'elasticapm': {
            'level': 'INFO',
            'class': 'elasticapm.contrib.django.handlers.LoggingHandler',
        },
        'sentry': {
            'level': 'INFO',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': RAVEN_CONFIG["dns"]
        }
    },
    'loggers': {
        'main': {
            'handlers': ['log_to_stdout', 'elasticapm'],
            'level': 'INFO',
            'propagate': True,
        },
        'sentry': {
            'handlers': ['sentry'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv("REDIS_BROKER_URL"),
        'TIMEOUT': 60 * 60 * 24,  # 24 hours
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor'
        }
    },
}

REDIS = {
    'default': (
        os.getenv("REDIS_HOST"),
        os.getenv("REDIS_PORT"),
        os.getenv("REDIS_DB"),
    ),
    'livecache': (
        os.getenv("REDIS_LIVECACHE_HOST"),
        os.getenv("REDIS_LIVECACHE_PORT"),
        os.getenv("REDIS_LIVECACHE_DB"),
    ),
}

REDIS_CLUSTER_ENABLED = False
REDIS_CLUSTER_NODES = [
    {
        "host": os.getenv("REDIS_CLUSTER_HOST"),
        "port": os.getenv("REDIS_CLUSTER_PORT")
    },
]

ELASTIC_APM = {
  # Set required service name. Allowed characters:
  # a-z, A-Z, 0-9, -, _, and space
  'SERVICE_NAME': '',

  # Use if APM Server requires a token
  'SECRET_TOKEN': '',

  # Set custom APM Server URL (default: http://localhost:8200)
  'SERVER_URL': '',
}
