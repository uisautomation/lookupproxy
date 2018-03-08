from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ['*']

STATIC_ROOT = '/usr/src/app/build/static'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE  # noqa: F405

# In production, use the production lookup
LOOKUP_API_ENDPOINT_HOST = 'www.lookup.cam.ac.uk'
