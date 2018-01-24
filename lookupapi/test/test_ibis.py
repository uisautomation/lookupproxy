from unittest import mock
from django.test import TestCase
from ucamlookup import ibisclient

from lookupapi import ibis


class IbisTests(TestCase):
    def test_get_connection(self):
        """Get connection should return a connection instance."""
        self.assertIsNotNone(ibis.get_connection())

    def test_person_methods_wrapper(self):
        """get_person_methods() should return a wrapped object which intercepts IbisExceptions."""

        with mock.patch('ucamlookup.ibisclient.PersonMethods') as person_methods:
            person_methods.return_value = MockPersonMethods()
            with self.assertRaises(ibis.IbisAPIException):
                ibis.get_person_methods().getPerson('crsid', 'test0001')

    def test_group_methods_wrapper(self):
        """get_group_methods() should return a wrapped object which intercepts IbisExceptions."""

        with mock.patch('ucamlookup.ibisclient.GroupMethods') as group_methods:
            group_methods.return_value = MockGroupMethods()
            with self.assertRaises(ibis.IbisAPIException):
                ibis.get_group_methods().getGroup('xxxx')

    def test_institution_methods_wrapper(self):
        """get_institution_methods() should return a wrapped object which intercepts
        IbisExceptions.

        """
        with mock.patch('ucamlookup.ibisclient.InstitutionMethods') as institution_methods:
            institution_methods.return_value = MockInstitutionMethods()
            with self.assertRaises(ibis.IbisAPIException):
                ibis.get_institution_methods().getInst('xxxx')


class MockPersonMethods:
    """A mock PersonMethods-like class which simply raises IbisException for all methods."""
    def getPerson(self, scheme, identifier, fetch=None):
        raise_ibis_exception()


class MockGroupMethods:
    """A mock GroupMethods-like class which simply raises IbisException for all methods."""
    def getGroup(self, groupid, fetch=None):
        raise_ibis_exception()


class MockInstitutionMethods:
    """A mock InstitutionMethods-like class which simply raises IbisException for all methods."""
    def getInst(self, instid, fetch=None):
        raise_ibis_exception()


def raise_ibis_exception():
    """Utility function which simply raises an IbisException."""
    raise ibisclient.IbisException(ibisclient.IbisError())
