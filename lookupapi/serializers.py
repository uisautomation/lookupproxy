"""
Django REST framework "serializers" for Lookup object.

"""
import base64
from rest_framework import serializers
from rest_framework.reverse import reverse


class Base64Field(serializers.Field):
    """Serialises binary data as base64."""
    def to_representation(self, obj):
        return base64.b64encode(obj)

    def to_internal_value(self, data):
        return base64.b64decode(data)


class FetchParametersSerializer(serializers.Serializer):
    """Serialise fetch parameters from a query string."""
    fetch = serializers.CharField(default=None, help_text=(
        'Comma-separated list of additional data to fetch for the resource. See '
        'https://www.lookup.cam.ac.uk/doc/ws-pydocs3/ibisclient.methods.PersonMethods.html and '
        'https://www.lookup.cam.ac.uk/doc/ws-pydocs3/ibisclient.methods.InstitutionMethods.html '
        'for details on the values this parameter can take.'))


class SearchParametersSerializer(FetchParametersSerializer):
    """Serialise search parameters from a query string."""
    query = serializers.CharField(help_text='The search string.')
    approxMatches = serializers.BooleanField(default=False, help_text=(
        'Flag to enable more approximate matching in the search, causing more results to be '
        'returned. Defaults to "false".'))
    includeCancelled = serializers.BooleanField(default=False, help_text=(
        'Flag to allow cancelled people to be included (people who are no longer members of '
        'the University). Defaults to "false".'))
    misStatus = serializers.ChoiceField(
        default=None, allow_null=True, choices=[
            ('staff', ('only people whose MIS status is "" (empty string), "staff", or '
                       '"staff,student"')),
            ('student', ('only people whose MIS status is set to "student" or "staff,student"')),
        ], help_text=(
            'The type of people to search for. If omitted, all matching people will be included. '
            'Note that the "staff" and "student" options are not mutually exclusive.'))
    attributes = serializers.CharField(default=None, allow_null=True, help_text=(
        'A comma-separated list of attributes to consider when searching. If this is omitted '
        'then all attribute schemes marked as searchable will be included.'))
    offset = serializers.IntegerField(
        default=0,
        help_text='The number of results to skip at the start of the search. Defaults to 0.')
    limit = serializers.IntegerField(
        default=100,
        help_text='The maximum number of results to return. Defaults to 100.')
    orderBy = serializers.ChoiceField(
        default='surname',
        choices=[('identifier', 'Primary Identifier'), ('surname', 'Surname')],
        help_text='The order in which to list the results. The default is "surname".')


class InstitutionListParametersSerializer(FetchParametersSerializer):
    """Serialise parameters the for the institution list endpoing."""
    includeCancelled = serializers.BooleanField(default=False, help_text=(
        'Flag to allow cancelled institutions. By default, only live institutions are returned.'))


class AttributeSchemeSerializer(serializers.Serializer):
    """Serializer for IbisAttributeScheme."""
    dataType = serializers.CharField(help_text='The attribute scheme\'s datatype.')
    displayName = serializers.CharField(
        help_text='The display name for labelling attributes in this scheme.')
    ldapName = serializers.CharField(help_text=(
        'The name of the attribute scheme in LDAP, if it is exported to LDAP. Note that many '
        'attributes are not exported to LDAP, in which case this name is typically just equal '
        'to the scheme\'s ID.'))
    multiLined = serializers.BooleanField(
        help_text='Flag for textual attributes schemes indicating whether they are multi-lined.')
    multiValued = serializers.BooleanField(
        help_text='Flag indicating whether attributes in this scheme can be multi-valued.')
    precedence = serializers.IntegerField(help_text=(
        'The attribute scheme\'s precedence. Methods that return or display attributes '
        'sort the results primarily in order of increasing values of attribute scheme '
        'precedence.'))
    regexp = serializers.CharField(help_text=(
        'For textual attributes, an optional regular expression that all attributes in this '
        'scheme match.'))
    schemeid = serializers.CharField(help_text='The unique identifier of the attribute scheme.')
    searchable = serializers.BooleanField(help_text=(
        'Flag indicating whether attributes of this scheme are searched by the default search '
        'functionality.'))


class PersonHyperlink(serializers.HyperlinkedIdentityField):
    """A field which can construct the appropriate link to a Person resource."""
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {'identifier': obj.identifier.value, 'scheme': obj.identifier.scheme}
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class PersonHyperlinkSerializer(serializers.Serializer):
    """Hyperlink-only serializer for IbisPerson objects."""
    url = PersonHyperlink(
        view_name='person-detail', help_text='Link to full resource.')


class GroupHyperlinkSerializer(serializers.Serializer):
    """Hyperlink-only serializer for IbisGroup objects."""
    url = serializers.HyperlinkedIdentityField(
        view_name='group-detail', lookup_field='groupid',
        help_text='Link to full resource.')


class InstitutionHyperlinkSerializer(serializers.Serializer):
    """Hyperlink-only serializer for IbisInstitution objects."""
    url = serializers.HyperlinkedIdentityField(
        view_name='institution-detail', lookup_field='instid',
        help_text='Link to full resource.')


class IdentifierSerializer(serializers.Serializer):
    """Serializer for IbisIdentifier objects."""
    scheme = serializers.CharField(help_text='The identifier\'s scheme (e.g., "crsid").')
    value = serializers.CharField(
        help_text='The identifier\'s value in that scheme (e.g., a specific CRSid value).')


class PersonSummarySerializer(PersonHyperlinkSerializer):
    """Serializer for IbisPerson objects."""
    cancelled = serializers.BooleanField(help_text='Flag indicating if the person is cancelled.')
    identifier = IdentifierSerializer(
        help_text='The person\'s primary identifier (typically their CRSid).')
    visibleName = serializers.CharField(help_text=(
        'The person\'s display name if that is visible, otherwise their registered name '
        'if that is visible, otherwise their surname if that is visible, otherwise the '
        'value of their primary identifier (typically their CRSid) which is always visible.'))


class GroupSummarySerializer(GroupHyperlinkSerializer):
    """Summary serializer for IbisGroup objects."""
    cancelled = serializers.BooleanField(help_text='Flag indicating if the group is cancelled.')
    description = serializers.CharField(help_text='The more detailed description of the group.')
    email = serializers.EmailField(help_text='The group\'s email address.')
    groupid = serializers.CharField(
        help_text='The group\'s numeric ID (actually a string e.g., "100656").')
    title = serializers.CharField(help_text='The group\'s title.')
    name = serializers.CharField(help_text='The group\'s unique name (e.g. "cs-editors").')


class InstitutionSummarySerializer(InstitutionHyperlinkSerializer):
    """Summary serializer for IbisInstitution."""
    acronym = serializers.CharField(help_text='The institutions\'s acronym, if set (e.g., "UCS").')
    cancelled = serializers.BooleanField(
        help_text='Flag indicating if the institution is cancelled.')
    instid = serializers.CharField(help_text='The institution\'s unique ID (e.g., "CS").')
    name = serializers.CharField(help_text='The institution\'s name.')


class AttributeSerializer(serializers.Serializer):
    """Serializer for IbisAttribute objects."""
    attrid = serializers.IntegerField(help_text='The unique internal identifier of the attribute.')
    binaryData = Base64Field(
        help_text='The binary data held in the attribute (e.g., a JPEG photo).')
    comment = serializers.CharField(help_text='Any comment associated with the attribute.')
    effectiveFrom = serializers.DateField(
        help_text='For time-limited attributes, the date from which it takes effect.')
    effectiveTo = serializers.DateField(
        help_text='For time-limited attributes, the date after which it is no longer effective.')
    instid = serializers.CharField(help_text=(
        'For a person attribute, the optional institution that the attribute is associated '
        'with. This will not be set for institution attributes.'))
    owningGroupid = serializers.CharField(help_text=(
        'For a person attribute, the ID of the group that owns it (typically the user agent '
        'group that created it).'))
    scheme = serializers.CharField(help_text='The attribute\'s scheme.')
    value = serializers.CharField(
        help_text='The attribute\'s value (except for binary attributes).')
    visibility = serializers.CharField(help_text=(
        'For a person attribute, it\'s visibility ("private", "institution", "university" or '
        '"world"). This will not be set for institution attributes.'))


class ContactPhoneNumberSerializer(serializers.Serializer):
    """Serializer for IbisContactPhoneNumber."""
    comment = serializers.CharField(help_text='Any comment associated with the phone number.')
    number = serializers.CharField(help_text='The phone number.')
    phoneType = serializers.CharField(help_text='The phone number\'s type.')


class ContactWebPageSerializer(serializers.Serializer):
    """Serializer for IbisContactWebPage."""
    label = serializers.CharField(help_text='The web page\'s label (link text) if set.')
    url = serializers.URLField(help_text='The web page\'s URL.')


class ContactRowSerializer(serializers.Serializer):
    """Serializer for IbisContactRow."""
    addresses = serializers.ListField(child=serializers.CharField(), help_text=(
        'A list of the contact row\'s addresses. This will never be null, but it may be an '
        'empty list.'))
    bold = serializers.BooleanField(
        help_text='Flag indicating if the contact row\'s text is normally displayed in bold.')
    description = serializers.CharField(help_text='The contact row\'s text.')
    emails = serializers.ListField(child=serializers.EmailField(), help_text=(
        'A list of the contact row\'s email addresses. This will never be null, but it may '
        'be an empty list.'))
    italic = serializers.BooleanField(
        help_text='Flag indicating if the contact row\'s text is normally displayed in italics.')
    people = PersonSummarySerializer(many=True, help_text=(
        'A list of the people referred to by the contact row. This will never be null, but it '
        'may be an empty list.'))
    phoneNumbers = ContactPhoneNumberSerializer(many=True, help_text=(
        'A list of the contact row\'s phone numbers. This will never be None, but it may be '
        'an empty list.'))
    webPages = ContactWebPageSerializer(many=True, help_text=(
        'A list of the contact row\'s web pages. This will never be None, but it may be an '
        'empty list.'))


class InstitutionSerializer(InstitutionSummarySerializer):
    """Serializer for IbisInstitution."""
    attributes = AttributeSerializer(many=True, help_text=(
        'A list of the institution\'s attributes. This will only be populated if the fetch '
        'parameter includes the "all_attrs" option, or any specific attribute schemes such as '
        '"email" or "address", or the special pseudo-attribute scheme "phone_numbers".'))
    contactRows = ContactRowSerializer(many=True, help_text=(
        'A list of the institution\'s contact rows. This will only be populated if the fetch '
        'parameter includes the "contact_rows" option.'))
    childInsts = InstitutionSummarySerializer(many=True, help_text=(
        'A list of the institution\'s child institutions. This will only be populated if the '
        'fetch parameter includes the "child_insts" option.'))
    members = PersonSummarySerializer(many=True, help_text=(
        'A list of the institution\'s members. This will only be populated if the fetch parameter '
        'includes the "all_members" option.'))
    parentInsts = InstitutionSummarySerializer(many=True, help_text=(
        'A list of the institution\'s parent institutions. This will only be populated if the '
        'fetch parameter includes the "parent_insts" option. Note: currently all institutions '
        'have one parent, but in the future institutions may have multiple parents.'))
    groups = GroupSummarySerializer(many=True, help_text=(
        'A list of all the groups that belong to the institution. This will only be populated if '
        'the fetch parameter includes the "inst_groups" option.'))
    managedByGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups that manage this institution. This will only be populated if the '
        'fetch parameter includes the "managed_by_groups" option.'))
    membersGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups that form the institution\'s membership. This will only be '
        'populated if the fetch parameter includes the "members_groups" option.'))


class GroupSerializer(GroupSummarySerializer):
    """Serializer for IbisGroup."""
    directMembers = PersonSummarySerializer(many=True, help_text=(
        'A list of the group\'s direct members, not including any members included via groups '
        'included by this group. This will only be populated if the fetch parameter includes the '
        '"direct_members" option.'))
    includedByGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups that directly include this group. Any members of this group will '
        'automatically be included in those groups (and recursively in any groups that include '
        'those groups). This will only be populated if the fetch parameter includes the '
        '"included_by_groups" option.'))
    includesGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups directly included in this group. Any members of the included groups '
        '(and recursively any groups that they include) will automatically be included in this '
        'group. This will only be populated if the fetch parameter includes the "includes_groups" '
        'option.'))
    managedByGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups that manage this group. This will only be populated if the fetch '
        'parameter includes the "managed_by_groups" option.'))
    managesInsts = InstitutionSerializer(many=True, help_text=(
        'A list of the institutions managed by this group. This will only be populated if the '
        'fetch parameter includes the "manages_insts" option.'))
    members = PersonSummarySerializer(many=True, help_text=(
        'A list of the group\'s members, including (recursively) any members of any included '
        'groups. This will only be populated if the fetch parameter includes the "all_members" '
        'option.'))
    membersOfInst = InstitutionSerializer(many=True, help_text=(
        'The details of the institution for which this group forms all or part of the membership. '
        'This will only be set for groups that are membership groups of institutions if the fetch '
        'parameter includes the "members_of_inst" option.'))
    owningInsts = InstitutionSerializer(many=True, help_text=(
        'A list of the institutions to which this group belongs. This will only be populated if '
        'the fetch parameter includes the "owning_insts" option.'))
    readByGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups that have privileged access to this group. Members of those groups '
        'will be able to read the members of this group, regardless of the membership '
        'visibilities. This will only be populated if the fetch parameter includes the '
        '"read_by_groups" option.'))
    readsGroups = GroupSummarySerializer(many=True, help_text=(
        'A list of the groups that this group has privileged access to. Members of this group '
        'will be able to read the members of any of those groups, regardless of the membership '
        'visibilities. This will only be populated if the fetch parameter includes the '
        '"reads_groups" option.'))


class PersonSerializer(PersonSummarySerializer):
    """Serializer for IbisPerson."""
    attributes = AttributeSerializer(many=True, help_text=(
        'A list of the person\'s attributes. This will only be populated if the fetch parameter '
        'includes the "all_attrs" option, or any specific attribute schemes such as "email" or '
        '"title", or the special pseudo-attribute scheme "phone_numbers".'))
    directGroups = GroupSerializer(many=True, help_text=(
        'A list of all the groups that the person directly belongs to. This does not include '
        'indirect group memberships - i.e., groups that include these groups. This will only be '
        'populated if the fetch parameter includes the "direct_groups" option.'))
    displayName = serializers.CharField(help_text='The person\'s display name (if visible).')
    groups = GroupSummarySerializer(many=True, help_text=(
        'A list of all the groups to which the person belongs, including indirect group '
        'memberships, via groups that include other groups. This will only be populated if the '
        'fetch parameter includes the "all_groups" option.'))
    identifiers = IdentifierSerializer(many=True, help_text=(
        'A list of the person\'s identifiers. This will only be populated if the fetch parameter '
        'included the "all_identifiers" option.'))
    institutions = InstitutionSummarySerializer(many=True, help_text=(
        'A list of all the institution\'s to which the person belongs. This will only be '
        'populated if the fetch parameter includes the "all_insts" option.'))
    isStaff = serializers.BooleanField(source='is_staff', help_text=(
        'Indicate if the person is a member of staff. Note that this tests for an misAffiliation '
        'of "", "staff" or "staff,student" since some members of staff will have a blank '
        'misAffiliation.'))
    isStudent = serializers.BooleanField(source='is_student', help_text=(
        'Indicate if the person is a student. This tests for an misAffiliation of "student" or '
        '"staff,student".'))
    misAffiliation = serializers.CharField(
        help_text='The person\'s MIS status ("staff", "student", "staff,student" or "").')
    registeredName = serializers.CharField(help_text='The person\'s registered name (if visible).')
    surname = serializers.CharField(help_text='The person\'s surname (if visible).')


class PersonListResultsSerializer(serializers.Serializer):
    """Serializer for person list results."""
    results = PersonSummarySerializer(many=True, help_text='Results of search')
    count = serializers.IntegerField(help_text='Total number of results available.')
    offset = serializers.IntegerField(help_text='0-based index of first result to return.')
    limit = serializers.IntegerField(help_text='Requested number of results.')


class AttributeSchemeListSerializer(serializers.Serializer):
    """Serializer for attribute scheme lists."""
    results = AttributeSchemeSerializer(many=True, help_text="List of attribute schemes")


class HealthSerializer(serializers.Serializer):
    """
    Health check response.

    """
    status = serializers.ChoiceField(choices=[('ok', 'ok')], help_text='Just the text "ok"')
