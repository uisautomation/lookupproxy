"""
Test that the registered system checks work as expected.

"""
from django.conf import settings
from django.core.management import call_command
# Q: is this a documented import location for SystemCheckError?
from django.core.management.base import SystemCheckError
from django.test import TestCase


class RequiredSettings(TestCase):
    """
    Required settings are set.

    """
    required_settings = [
        'LOOKUP_API_OAUTH2_TOKEN_URL',
        'LOOKUP_API_OAUTH2_INTROSPECT_URL',
        'LOOKUP_API_OAUTH2_CLIENT_ID',
        'LOOKUP_API_OAUTH2_CLIENT_SECRET',
        'LOOKUP_API_OAUTH2_INTROSPECT_SCOPES',
    ]

    def test_checks_pass(self):
        """The system checks should succeed in the test suite configuration."""
        call_command('check')

    def test_checks_fail(self):
        """The system check should fail if any required setting is unset or blank."""
        for name in self.required_settings:
            with self.settings(**{name: ''}), self.assertRaises(SystemCheckError):
                call_command('check')
            with self.settings(**{name: None}), self.assertRaises(SystemCheckError):
                call_command('check')
