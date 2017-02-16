from copy import deepcopy

from lxml import etree
import pytest

from codalib import bagatom


@pytest.fixture(scope='module')
def person_xml():
    return """<?xml version="1.0"?>
        <person xmlns="http://example.com/namespace">
            <firstName>James</firstName>
            <lastName>Doe</lastName>
            <nickname>Jim</nickname>
        </person>
    """


@pytest.fixture(scope='module')
def event_atom():
    return """<?xml version="1.0"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
        <title>Atom-Powered Robots Run Amok</title>
        <link href="http://example.org/2003/12/13/atom03" />
        <link rel="alternate" type="text/html" href="http://example.org/2003/12/13/atom03.html"/>
        <link rel="edit" href="http://example.org/2003/12/13/atom03/edit"/>
        <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
        <updated>2003-12-13T18:30:02Z</updated>
        <summary>Some text.</summary>
        <content>
            <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
                <premis:eventIdentifier>
                    <premis:eventIdentifierType>
                        http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID
                    </premis:eventIdentifierType>
                    <premis:eventIdentifierValue>
                        9e42cbd3cc3b4dfc888522036bbc4491
                    </premis:eventIdentifierValue>
                </premis:eventIdentifier>
                <premis:eventType>
                    http://purl.org/net/untl/vocabularies/preservationEvents/#fixityCheck
                </premis:eventType>
                <premis:eventDateTime>2013-05-13T14:14:55Z</premis:eventDateTime>
                <premis:eventDetail>THIS IS EDITING THE EVENT DETAIL</premis:eventDetail>
                <premis:eventOutcomeInformation>
                    <premis:eventOutcome>
                        http://purl.org/net/untl/vocabularies/eventOutcomes/#success
                    </premis:eventOutcome>
                    <premis:eventOutcomeDetail>
                        <premis:eventOutcomeDetailNote>
                            Total time for verification: 0:00:01.839590
                        </premis:eventOutcomeDetailNote>
                    </premis:eventOutcomeDetail>
                </premis:eventOutcomeInformation>
                <premis:linkingAgentIdentifier>
                    <premis:linkingAgentIdentifierType>
                        http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL
                    </premis:linkingAgentIdentifierType>
                    <premis:linkingAgentIdentifierValue>
                        http://localhost:8787/agent/codaMigrationVerification
                    </premis:linkingAgentIdentifierValue>
                </premis:linkingAgentIdentifier>
                <premis:linkingObjectIdentifier>
                    <premis:linkingObjectIdentifierType>
                        http://purl.org/net/untl/vocabularies/identifier-qualifiers/#ARK
                    </premis:linkingObjectIdentifierType>
                    <premis:linkingObjectIdentifierValue>
                        ark:/67531/coda10kx
                    </premis:linkingObjectIdentifierValue>
                    <premis:linkingObjectRole/>
                </premis:linkingObjectIdentifier>
            </premis:event>
        </content>
    </entry>
    """


@pytest.fixture(scope='module')
def mini_mock():
    """
    Allows the tests to assert more accurately about the state of the
    object's properties than a full-blown mock allows.
    """
    class MiniMock(object):

        def __init__(self, **kwargs):
            pass

    return MiniMock


def test_object_properties_match_xml(person_xml, mini_mock):
    """
    Test the object is modified to include attributes for elements
    from the XML tree.
    """
    tree = etree.fromstring(person_xml)

    # Set up some blank object attributes.
    person0 = mini_mock()
    person0.nickname = None
    person0.first_name = None

    person1 = mini_mock()
    person1.nickname = None
    person1.first_name = None

    # The mappings for XML -> Object translation. This will tell the function
    # to get the firstName element and assign it to the first_name attribute on
    # the object. It will do the same for nickname.
    mapping = {
        '@namespaces': {'x': 'http://example.com/namespace'},
        'nickname': ['x:nickname'], 'first_name': ['x:firstName']
    }
    bagatom.updateObjectFromXML(tree, person1, mapping)

    assert person0.nickname != person1.nickname
    assert person0.first_name != person1.first_name
    assert person1.nickname == 'Jim'
    assert person1.first_name == 'James'


def test_object_does_not_have_xml_property(person_xml, mini_mock):
    """
    Check that an attribute is added to the object when the object
    does not have the attribute specified in the updateList.
    """
    tree = etree.fromstring(person_xml)

    # We will not setup the mock this time to verify that the function
    # will still add those attributes.
    person = mini_mock()

    mapping = {
        '@namespaces': {'x': 'http://example.com/namespace'},
        'nickname': ['x:nickname']}
    bagatom.updateObjectFromXML(tree, person, mapping)

    assert person.nickname == 'Jim'


def test_xml_does_not_have_property(person_xml, mini_mock):
    """
    Verify that an attribute is not added to the object when the
    updateList maps to an XML element that is not included in the tree.
    """
    tree = etree.fromstring(person_xml)

    person = mini_mock()

    # The phone element does not exist in the XML that is being passed into
    # updateObjectFromXML.
    mapping = {
        '@namespaces': {'x': 'http://example.com/namespace'},
        'phone': ['x:phone']
    }
    bagatom.updateObjectFromXML(tree, person, mapping)

    assert hasattr(person, 'phone') is False


def test_object_returns_unmodified(person_xml, mini_mock):
    """
    Check the object returns unmodified if the updateList dictionary
    is empty.
    """
    tree = etree.fromstring(person_xml)

    person0 = mini_mock()
    person1 = mini_mock()

    mapping = {}
    bagatom.updateObjectFromXML(tree, person1, mapping)
    assert person0.__dict__ == person1.__dict__


def test_mapping_w_namespaces(event_atom):
    """
    Check that properties are mapped as expected from xml documents
    with multiple namespaces.
    """
    atom_tree = etree.fromstring(event_atom)
    event_tree = atom_tree.xpath(
        '//atom:content/premis:event', namespaces={
            'atom': 'http://www.w3.org/2005/Atom',
            'premis': 'info:lc/xmlns/premis-v2'
        }
    )
    event_tree = event_tree[0]
    map_dict = {}
    map_dict['@namespaces'] = {
        'premis': 'info:lc/xmlns/premis-v2'
    }
    map_dict['event_outcome'] = 'premis:eventOutcomeInformation' +\
        '/premis:eventOutcome'
    map_dict['event_outcome_detail'] = 'premis:eventOutcomeInformation' +\
        '/premis:eventOutcomeDetail/premis:eventOutcomeDetailNote'
    expected = 'http://purl.org/net/untl/vocabularies/eventOutcomes/#success'
    event = mini_mock()
    bagatom.updateObjectFromXML(event_tree, event, map_dict)
    assert expected == event.event_outcome.strip()
