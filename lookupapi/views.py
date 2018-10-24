"""
Views for :py:mod:`lookupapi`.

"""
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.response import Response
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from ucamlookup import ibisclient, re
from . import ibis
from . import serializers
from automationoauthdrf.authentication import OAuth2TokenAuthentication
from .permissions import HasScopesPermission


# TODO: once the API has settled a little, these resource views can be re-factored into a generic
# view and sub-classes.


REQUIRED_SCOPES = ['lookup:anonymous']
"""
List of OAuth2 scopes requires to access the Lookup API.

"""


def _get_or_404(obj):
    """Raise a HTTP 404 NotFound if obj is None otherwise return obj."""
    if obj is None:
        raise Http404
    return obj


class ViewPermissionsMixin:
    """
    A mixin class which specifies the authentication and permissions for all API endpoints.

    """
    authentication_classes = (OAuth2TokenAuthentication,)
    permission_classes = (HasScopesPermission,)
    required_scopes = REQUIRED_SCOPES


class PersonFetchAttributes(generics.RetrieveAPIView):
    """
    All valid attributes for a person.

    """
    serializer_class = serializers.AttributeSchemeListSerializer

    def get_object(self):
        return {'results': ibis.get_person_methods().allAttributeSchemes()}


class InstitutionFetchAttributes(generics.RetrieveAPIView):
    """
    All valid attributes for a institution.

    """
    serializer_class = serializers.AttributeSchemeListSerializer

    def get_object(self):
        return {'results': ibis.get_institution_methods().allAttributeSchemes()}


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=serializers.SearchParametersSerializer(),
    operation_security=[{'oauth2': REQUIRED_SCOPES}],
))
class PersonList(ViewPermissionsMixin, generics.ListAPIView):
    """
    Search for people using a free text query string. This is the same search function that is used
    in the Lookup web application. By default, only a few basic details about each person are
    returned, but the optional fetch parameter may be used to fetch additional attributes or
    references.

    """
    serializer_class = serializers.PersonListResultsSerializer

    count_query_keys = ['query', 'approxMatches', 'includeCancelled', 'misStatus', 'attributes']
    """Query keys which are used by both searchCount and search."""

    full_query_keys = ['offset', 'limit', 'fetch', 'orderBy']
    """Query keys which are used only by search."""

    def list(self, request):
        query = serializers.SearchParametersSerializer(request.query_params).data
        kwargs = {key: query.get(key) for key in self.count_query_keys}
        count = ibis.get_person_methods().searchCount(**kwargs)
        kwargs.update({key: query.get(key) for key in self.full_query_keys})
        results = ibis.get_person_methods().search(**kwargs)
        return Response(self.serializer_class({
            'results': results, 'count': count, 'offset': query['offset'], 'limit': query['limit']
        }, context={'request': request}).data)


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=serializers.FetchParametersSerializer(),
    operation_security=[{'oauth2': REQUIRED_SCOPES}],
    manual_parameters=[
        Parameter(
            name='scheme', in_='path', required=True, type='string', description=(
                'Identifier scheme used to identify the person. Typically this will be "crsid".')),
        Parameter(
            name='identifier', in_='path', required=True, type='string', description=(
                'Identifier of the person in the given scheme. For example, in the "crsid" scheme '
                'this will be the crsid of the person.')),
    ],
))
class Person(ViewPermissionsMixin, generics.RetrieveAPIView):
    """
    Retrieve information on a person by scheme and identifier within that scheme. The scheme is
    usually "crsid" and the identifier is usually that person's crsid.

    If the scheme is "mock" then data from the test user mug99 is returned with the
    corresponding identifier from the API call.

    If the scheme "token" and identifier "self" is used then if the user has been authenticated
    it will return the lookup data of the authenticated user.

    """
    serializer_class = serializers.PersonSerializer

    def get_object(self):
        query = serializers.FetchParametersSerializer(self.request.query_params)
        scheme = self.kwargs['scheme']
        identifier = self.kwargs['identifier']
        fetch = query.data['fetch']

        if scheme == "token" and identifier == "self":
            if self.request.user.is_authenticated:
                # Historically we have used both ':' and '+' as a record separator in usernames to
                # record scheme and identifier. We have also used bare crsids. Attempt to support
                # all of these things.
                username = self.request.user.username
                if ':' in username:
                    scheme, identifier = username.split(':')
                elif '+' in username:
                    scheme, identifier = username.split('+')
                else:
                    scheme, identifier = 'crsid', username
            else:
                raise Http404("You are not authenticated")

        if scheme == "mock" and re.match('test0([0-4]\d\d|500)', identifier):
            # Returns a mocked lookup entry for a Person (test user mug99)
            person = ibis.get_person_methods().getPerson("crsid", "mug99", fetch)
            person.identifier = ibisclient.IbisIdentifier({'scheme': scheme, 'value': identifier})
            person.identifier.value = identifier
            if hasattr(person, "identifiers"):
                person.identifiers = \
                    [ibisclient.IbisIdentifier({'scheme': scheme, 'value': identifier})]
                person.identifiers[0].value = identifier
            # Following raven recommendations: "User-ids test0001 to test0400 are marked as
            # belonging to 'current staff and students', leaving user-ids test0401 to test0500 not
            # so marked"
            if re.match('test0(40[1-9]|4[1-9]\d|500)', identifier):
                # This is the only way to have isStaff returning False, misAffiliation returns
                # isStaff=True as some members of staff have this
                person.misAffiliation = "student"
            return person

        return _get_or_404(ibis.get_person_methods().getPerson(scheme, identifier, fetch))


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=serializers.FetchParametersSerializer(),
    operation_security=[{'oauth2': REQUIRED_SCOPES}],
))
class Group(ViewPermissionsMixin, generics.RetrieveAPIView):
    """
    Retrieve information on a group by groupid.

    """
    serializer_class = serializers.GroupSerializer

    def get_object(self):
        query = serializers.FetchParametersSerializer(self.request.query_params)
        return _get_or_404(ibis.get_group_methods().getGroup(
            self.kwargs['groupid'], query.data['fetch']))


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=serializers.InstitutionListParametersSerializer(),
    operation_security=[{'oauth2': REQUIRED_SCOPES}],
))
class InstitutionList(ViewPermissionsMixin, generics.ListAPIView):
    """
    Return a list of all institutions known to Lookup.

    """
    serializer_class = serializers.InstitutionListResultsSerializer

    def list(self, request):
        query = serializers.InstitutionListParametersSerializer(self.request.query_params).data
        results = ibis.get_institution_methods().allInsts(
            includeCancelled=query['includeCancelled'], fetch=query['fetch'])
        return Response(self.serializer_class(
            {'results': results}, context={'request': request}).data)


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=serializers.FetchParametersSerializer(),
    operation_security=[{'oauth2': REQUIRED_SCOPES}],
))
class Institution(ViewPermissionsMixin, generics.RetrieveAPIView):
    """
    Retrieve information on an institution by instid.

    """
    serializer_class = serializers.InstitutionSerializer

    def get_object(self):
        query = serializers.FetchParametersSerializer(self.request.query_params)
        return _get_or_404(ibis.get_institution_methods().getInst(
            self.kwargs['instid'], query.data['fetch']))


class Health(generics.RetrieveAPIView):
    """
    Returns a HTTP 200 response when the application is running. Can be used as a readiness
    probe.

    """
    serializer_class = serializers.HealthSerializer

    def get_object(self):
        return {'status': 'ok'}
