"""
The :py:mod:`lookupapi` application ships with some custom system checks which ensure that the
``LOOKUP_API_OAUTH2_...`` settings have non-default values. These system checks are registered by
the :py:class:`~lookupapi.apps.LookupAPIConfig` class's
:py:meth:`~lookupapi.apps.LookupAPIConfig.ready` method.

.. seealso::

    The `Django System Check Framework <https://docs.djangoproject.com/en/2.0/ref/checks/>`_.

"""
from django.conf import settings
from django.core.checks import register, Error


@register
def api_credentials_check(app_configs, **kwargs):
    """
    A system check ensuring that the OAuth2 credentials are specified.

    .. seealso:: https://docs.djangoproject.com/en/2.0/ref/checks/

    """
    errors = []

    # Check that all required settings are specified and non-None
    required_settings = [
        'LOOKUP_API_OAUTH2_TOKEN_URL',
        'LOOKUP_API_OAUTH2_INTROSPECT_URL',
        'LOOKUP_API_OAUTH2_CLIENT_ID',
        'LOOKUP_API_OAUTH2_CLIENT_SECRET',
        'LOOKUP_API_OAUTH2_INTROSPECT_SCOPES',
    ]
    for idx, name in enumerate(required_settings):
        value = getattr(settings, name, None)
        if value is None or value == '':
            errors.append(Error(
                'Required setting {} not set'.format(name),
                id='lookupapi.E{:03d}'.format(idx + 1),
                hint='Add {} to settings.'.format(name)))

    return errors
