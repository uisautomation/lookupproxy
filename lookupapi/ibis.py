"""
Convenience functions for accessing Ibis (aka "Lookup") APIs.

"""
import functools
import inspect
from django.conf import settings
from rest_framework.exceptions import APIException

from ucamlookup import ibisclient


def get_connection():
    """
    Return an IbisClientConnection instance based upon the current settings.

    .. seealso:: The :py:mod:`~.defaultsettings` module.

    """
    return ibisclient.IbisClientConnection(
        settings.LOOKUP_API_ENDPOINT_HOST,
        settings.LOOKUP_API_ENDPOINT_PORT,
        settings.LOOKUP_API_ENDPOINT_BASE,
        settings.LOOKUP_API_ENDPOINT_VERIFY
    )


def get_person_methods(connection=None):
    """
    Return a PersonMethods instance for the specified IbisClientConnection. If the connection is
    None then :py:func:`~.get_connection` is used to get a connection.

    The returned instance has all of its callable attributes decorated with the
    :py:func:`ibis_exception_wrapper` decorator.

    """
    connection = connection if connection is not None else get_connection()
    return _decorate_methods(ibisclient.PersonMethods(connection), ibis_exception_wrapper)


def get_group_methods(connection=None):
    """
    Return a GroupMethods instance for the specified IbisClientConnection. If the connection is
    None then :py:func:`~.get_connection` is used to get a connection.

    The returned instance has all of its callable attributes decorated with the
    :py:func:`ibis_exception_wrapper` decorator.

    """
    connection = connection if connection is not None else get_connection()
    return _decorate_methods(ibisclient.GroupMethods(connection), ibis_exception_wrapper)


def get_institution_methods(connection=None):
    """
    Return a InstitutionMethods instance for the specified IbisClientConnection. If the connection
    is None then :py:func:`~.get_connection` is used to get a connection.

    The returned instance has all of its callable attributes decorated with the
    :py:func:`ibis_exception_wrapper` decorator.

    """
    connection = connection if connection is not None else get_connection()
    return _decorate_methods(ibisclient.InstitutionMethods(connection), ibis_exception_wrapper)


class IbisAPIException(APIException):
    """
    A custom Django REST Framework :py:class:`APIException` sub-class which marshals an
    :py:class:`IbisException` into a form the DRF can understand.

    """
    def __init__(self, ibis_exception):
        self.error = ibis_exception.get_error()
        self.detail = self.error.message
        self.code = self.error.code

    def get_full_details(self):
        details = super().get_full_details()
        details['details'] = self.error.details


def ibis_exception_wrapper(f):
    """
    Function or method decorator which intercepts :py:class:`IbisException` errors and re-raises
    them as :py:class:`~.IbisAPIException` instances.

    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ibisclient.IbisException as e:
            raise IbisAPIException(e)
    return wrapper


def _decorate_methods(obj, decorator):
    """
    Inspect a live Python object and decorate all of its methods with the passed decorator. Return
    the decorated object.

    """
    for name, value in inspect.getmembers(obj, inspect.ismethod):
        setattr(obj, name, decorator(value))
    return obj
