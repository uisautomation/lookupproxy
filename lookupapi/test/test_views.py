"""
Test API views.

"""
import urllib.parse
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from ucamlookup import ibisclient

from lookupapi.views import REQUIRED_SCOPES


class ViewTestCase:
    """
    Convenience abstract base class for view tests.

    """
    view_name = ''
    view_kwargs = {}
    view_args = []
    default_query = None

    def setUp(self):
        # Patch Lookup api get-ers
        self.get_person_methods_patch = mock.patch('lookupapi.ibis.get_person_methods')
        self.get_person_methods = self.get_person_methods_patch.start()
        self.get_group_methods_patch = mock.patch('lookupapi.ibis.get_group_methods')
        self.get_group_methods = self.get_group_methods_patch.start()
        self.get_institution_methods_patch = mock.patch('lookupapi.ibis.get_institution_methods')
        self.get_institution_methods = self.get_institution_methods_patch.start()

    def tearDown(self):
        self.get_person_methods_patch.stop()
        self.get_group_methods_patch.stop()
        self.get_institution_methods_patch.stop()

    def get(self, query=None):
        """HTTP GET a typical URL for this view."""
        url = reverse(self.view_name, args=self.view_args, kwargs=self.view_kwargs)
        if query is None:
            query = self.default_query
        if query is not None:
            url = urllib.parse.urljoin(url, '?' + urllib.parse.urlencode(query))
        return self.client.get(url)


class AuthenticatedViewTestCase(ViewTestCase):
    """
    Convenience abstract base class for view tests which checks basic authorisation.

    """
    required_scopes = REQUIRED_SCOPES

    def setUp(self):
        super().setUp()
        self.auth_patch = self.patch_authenticate()
        self.mock_authenticate = self.auth_patch.start()
        # By default, authentication succeeds
        user = get_user_model().objects.create_user(username="mock:test0001")
        self.mock_authenticate.return_value = (user, {'scope': ' '.join(self.required_scopes)})

    def tearDown(self):
        self.auth_patch.stop()
        super().tearDown()

    def test_no_auth_fails(self):
        """Passing no authorisation fails."""
        self.mock_authenticate.return_value = None
        response = self.get()
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.has_header('www-authenticate'))

    def test_no_scope_fails(self):
        """Passing authorisation with incorrect scopes fail."""
        self.mock_authenticate.return_value = (None, {'scope': 'not right'})
        self.assertEqual(self.get().status_code, 403)

    def test_correct_scope_fails(self):
        """Passing authorisation with correct scopes succeed."""
        self.assertEqual(self.get().status_code, 200)

    def patch_authenticate(self, return_value=None):
        """Patch authentication's authenticate function."""
        mock_authenticate = mock.MagicMock()
        mock_authenticate.return_value = return_value

        return mock.patch(
            'oauthcommon.authentication.OAuth2TokenAuthentication.authenticate', mock_authenticate)


class PersonByCRSIDTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'person-detail'
    view_kwargs = {'scheme': 'crsid', 'identifier': 'spqr2'}

    def test_not_found(self):
        self.get_person_methods.return_value.getPerson.return_value = None
        self.assertEqual(self.get().status_code, 404)

    def test_found(self):
        person = self.create_person()
        self.get_person_methods.return_value.getPerson.return_value = person
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('displayName'), person.displayName)

    def create_person(self):
        person = ibisclient.IbisPerson()
        person.displayName = 'Testing1'
        person.identifier = ibisclient.IbisIdentifier({'scheme': 'crsid', 'value': 'spqr2'})
        return person


class PersonMockedTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'person-detail'
    view_kwargs = {'scheme': 'mock', 'identifier': 'test0005'}

    def test_found_staff(self):
        self.view_kwargs['identifier'] = "test0005"
        person = self.create_person()
        self.get_person_methods.return_value.getPerson.return_value = person
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        import sys
        sys.stdout.write(str(data))
        self.assertEqual(data['identifier']['value'], "test0005")
        self.assertEqual(data['identifier']['scheme'], "mock")
        self.assertTrue(data['isStaff'])

    def test_found_no_staff(self):
        self.view_kwargs['identifier'] = "test0405"
        person = self.create_person()
        self.get_person_methods.return_value.getPerson.return_value = person
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['identifier']['value'], "test0405")
        self.assertEqual(data['identifier']['scheme'], "mock")
        self.assertFalse(data['isStaff'])

    def create_person(self):
        person = ibisclient.IbisPerson()
        person.displayName = 'Testing1'
        person.identifier = ibisclient.IbisIdentifier({'scheme': 'crsid', 'value': 'mug99'})
        person.identifier.value = 'mug99'
        return person


class PersonSelfTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'person-detail'
    view_kwargs = {'scheme': 'token', 'identifier': 'self'}

    def test_found(self):
        person = self.create_person()
        self.get_person_methods.return_value.getPerson.return_value = person
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('displayName'), person.displayName)

    def create_person(self):
        person = ibisclient.IbisPerson()
        person.displayName = 'Testing1'
        person.identifier = ibisclient.IbisIdentifier({'scheme': 'crsid', 'value': 'test0001'})
        return person


class PersonListTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'person-list'
    default_query = {'query': 'xxx'}

    def setUp(self):
        super().setUp()

        # By default, return no results
        self.set_return_value([])

    def test_empty_list(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('results'), [])
        self.assertEqual(data.get('count'), 0)

    def set_return_value(self, return_value):
        self.get_person_methods.return_value.search.return_value = return_value
        self.get_person_methods.return_value.searchCount.return_value = len(return_value)

    def create_person(self, crsid):
        person = ibisclient.IbisPerson()
        person.displayName = '{} USER'.format(crsid)
        person.identifier = ibisclient.IbisIdentifier({'scheme': 'crsid', 'value': crsid})
        return person


class InstitutionListTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'institution-list'

    def setUp(self):
        super().setUp()

        # By default, return no results
        self.set_return_value([])

    def test_empty_list(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('results'), [])

    def test_multiple_reponse(self):
        """Multiple institutions should return correctly."""
        inst_list = [
            self.create_institution('TESTA'),
            self.create_institution('TESTB'),
        ]
        self.set_return_value(inst_list)
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), len(inst_list))
        for received, expected in zip(data['results'], inst_list):
            self.assertEqual(received['name'], expected.name)
            self.assertEqual(received['instid'], expected.instid)

    def test_no_query_params(self):
        """Passing no query passes correct default values to allInsts"""
        self.get()
        self.mocked_allInsts.assert_called_with(includeCancelled=False, fetch=None)

    def test_include_cancelled_param(self):
        """Passing includeCancelled as query is passed to allInsts"""
        self.get({'includeCancelled': 'true'})
        self.mocked_allInsts.assert_called_with(includeCancelled=True, fetch=None)

    def test_fetch_param(self):
        """Passing fetch as query is passed to allInsts"""
        self.get({'fetch': 'foo,bar'})
        self.mocked_allInsts.assert_called_with(includeCancelled=False, fetch='foo,bar')

    def set_return_value(self, return_value):
        self.mocked_allInsts.return_value = return_value

    @property
    def mocked_allInsts(self):
        return self.get_institution_methods.return_value.allInsts

    def create_institution(self, instid):
        institution = ibisclient.IbisInstitution()
        institution.instid = instid
        institution.name = 'Institution ' + instid
        return institution


class GroupTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'group-detail'
    view_kwargs = {'groupid': '102030'}

    def test_not_found(self):
        self.get_group_methods.return_value.getGroup.return_value = None
        self.assertEqual(self.get().status_code, 404)

    def test_found(self):
        group = self.create_group()
        self.get_group_methods.return_value.getGroup.return_value = group
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(data)
        self.assertEqual(data.get('name'), group.name)

    def create_group(self):
        group = ibisclient.IbisGroup()
        group.name = 'Testing1'
        return group


class InstitutionTest(AuthenticatedViewTestCase, TestCase):
    view_name = 'institution-detail'
    view_kwargs = {'instid': '102030'}

    def test_not_found(self):
        self.get_institution_methods.return_value.getInst.return_value = None
        self.assertEqual(self.get().status_code, 404)

    def test_found(self):
        institution = self.create_institution()
        self.get_institution_methods.return_value.getInst.return_value = institution
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(data)
        self.assertEqual(data.get('name'), institution.name)

    def create_institution(self):
        institution = ibisclient.IbisInstitution()
        institution.name = 'Testing1'
        return institution


class SwaggerAPITest(ViewTestCase, TestCase):
    view_name = 'schema-json'
    view_kwargs = {'format': '.json'}

    def test_security_definitions(self):
        """API spec should define an oauth2 security requirement."""
        spec = self.get_spec()
        self.assertIn('securityDefinitions', spec)
        self.assertIn('oauth2', spec['securityDefinitions'])

    def get_spec(self):
        """Return the Swagger (OpenAPI) spec as parsed JSON."""
        response = self.get()
        self.assertEqual(response.status_code, 200)
        return response.json()


class PersonAttributesTest(ViewTestCase, TestCase):
    view_name = 'person-attributes'

    def test_empty_list(self):
        self.get_person_methods.return_value.allAttributeSchemes.return_value = []
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('results'), [])


class InstitutionAttributesTest(ViewTestCase, TestCase):
    view_name = 'institution-attributes'

    def test_empty_list(self):
        self.get_institution_methods.return_value.allAttributeSchemes.return_value = []
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('results'), [])


class HealthTest(ViewTestCase, TestCase):
    view_name = 'healthz'

    def test_gettable(self):
        """Health check endpoint should return 200 status."""
        self.assertEqual(self.get().status_code, 200)
