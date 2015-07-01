from copy import deepcopy

from lxml import etree
from mock import Mock
import pytest

from codalib import bagatom


@pytest.fixture(scope='module')
def person_xml():
    return """<person xmlns="http://example.com/namespace">
                  <firstName>James</firstName>
                  <lastName>Doe</lastName>
                  <nickname>Jim</nickname>
              </person>
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
    return_object = mini_mock()
    return_object.nickname = None
    return_object.first_name = None

    # A mock function for the XMLToObjectFunc parameter. We will make a copy of
    # the object to return to ensure that we do not mutate it in the test.
    xmlToObject = Mock(return_value=deepcopy(return_object))

    # The mappings for XML -> Object translation. This will tell the function
    # to get the firstName element and assign it to the first_name attribute on
    # the object. It will do the same for nickname.
    updateList = {'nickname': ['nickname'], 'first_name': ['firstName']}
    updated_object = bagatom.updateObjectFromXML(
        tree, xmlToObject, None, None, updateList)

    assert updated_object.nickname == 'Jim'
    assert updated_object.first_name == 'James'


def test_object_does_not_have_xml_property(person_xml, mini_mock):
    """
    Check that an attribute is added to the object when the object
    does not have the attribute specified in the updateList.
    """
    tree = etree.fromstring(person_xml)

    # We will not setup the mock this time to verify that the function
    # will still add those attributes.
    return_object = mini_mock()
    xmlToObject = Mock(return_value=deepcopy(return_object))

    updateList = {'nickname': ['nickname']}
    updated_object = bagatom.updateObjectFromXML(
        tree, xmlToObject, None, None, updateList)

    assert updated_object.nickname == 'Jim'


def test_xml_does_not_have_property(person_xml, mini_mock):
    """
    Verify that an attribute is not added to the object when the
    updateList maps to an XML element that is not included in the tree.
    """
    tree = etree.fromstring(person_xml)

    return_object = mini_mock()
    xmlToObject = Mock(return_value=deepcopy(return_object))

    # The phone element does not exist in the XML that is being passed into
    # updateObjectFromXML.
    updateList = {'phone': ['phone']}
    updated_object = bagatom.updateObjectFromXML(
        tree, xmlToObject, None, None, updateList)

    # Assert that the returned object does not include the phone attribute.
    assert hasattr(updated_object, 'phone') is False


def test_object_returns_unmodified(person_xml, mini_mock):
    """
    Check the object returns unmodified if the updateList dictionary
    is empty.
    """
    tree = etree.fromstring(person_xml)

    return_object = mini_mock()
    xmlToObject = Mock(return_value=deepcopy(return_object))

    updateList = {}
    updated_object = bagatom.updateObjectFromXML(
        tree, xmlToObject, None, None, updateList)

    assert dir(updated_object) == dir(return_object)
