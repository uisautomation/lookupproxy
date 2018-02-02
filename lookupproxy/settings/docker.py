from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ['*']

STATIC_ROOT = '/usr/src/app/build/static'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE  # noqa: F405
