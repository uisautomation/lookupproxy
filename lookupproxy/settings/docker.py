from .base import *  # noqa: F403
import os

DEBUG = False
ALLOWED_HOSTS = ['*']

STATIC_ROOT = '/usr/src/app/build/static'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE  # noqa: F405

# In production, use the production lookup
LOOKUP_API_ENDPOINT_HOST = 'www.lookup.cam.ac.uk'

# Load OAuth2 settings from environment if present
OAUTH2_TOKEN_URL = os.environ.get('OAUTH2_TOKEN_URL', None)
OAUTH2_INTROSPECT_URL = os.environ.get('OAUTH2_INTROSPECT_URL', None)
OAUTH2_CLIENT_ID = os.environ.get('OAUTH2_CLIENT_ID', None)
OAUTH2_CLIENT_SECRET = os.environ.get('OAUTH2_CLIENT_SECRET', None)
OAUTH2_INTROSPECT_SCOPES = os.environ.get('OAUTH2_INTROSPECT_SCOPES', '').split(' ')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(pathname)s:%(lineno)d '
                       '%(funcName)s "%(message)s"')
        },
        'simple': {
            'format': '%(levelname)s "%(message)s"'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO'
        },
    }
}
