from datetime import datetime

from lxml import etree
import pytest

from codalib import util
from codalib.xsdatetime import xsDateTime_format
import os


SCHEMA_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'schema'
)


@pytest.fixture()
def premis_schema():
    """Provides an lxml schema object for the Premis v2 XSD suitable
    for validation.
    """
    schema_file = open(os.path.join(SCHEMA_DIR, "premis-v2-3.xsd"))
    schema_doc = etree.parse(schema_file)
    schema = etree.XMLSchema(schema_doc)

    return schema


@pytest.fixture()
def premis_args():
    return dict(
        eventType='big event',
        agentIdentifier='me',
        eventDetail='details of my event',
        eventOutcome='huge success',
        outcomeDetail='lots of music',
        eventIdentifier='1102 ave B.',
        linkObjectList=['abc', 'bcd'],
        eventDate=datetime(2015, 01, 01)
    )


def test_validate_eventxml(premis_args, premis_schema):
    """
    Check produced PREMIS Event xml against schema
    """
    premis = util.createPREMISEventXML(**premis_args)
    premis_schema.assert_(premis)


def test_return_value(premis_args):
    """
    Check the return value is an etree._Element instance.
    """
    premis = util.createPREMISEventXML(**premis_args)
    assert isinstance(premis, etree._Element)


def test_with_empty_outcomeDetail_argument(premis_args):
    """
    Check the function is successful without the outcomeDetail
    kwarg.
    """
    premis_args.pop('outcomeDetail')
    util.createPREMISEventXML(**premis_args)


def test_with_empty_eventIdentifier_arguments(premis_args):
    """
    Check the function is successful without the eventIdentifier
    kwarg.
    """
    premis_args.pop('eventIdentifier')
    util.createPREMISEventXML(**premis_args)


def test_with_empty_linkObjectList_arguments(premis_args):
    """
    Check the function is successful without the linkObjectList
    kwarg.
    """
    premis_args.pop('linkObjectList')
    util.createPREMISEventXML(**premis_args)


def test_with_empty_eventDate_arguments(premis_args):
    """
    Check the function is successful without the eventDate
    kwarg.
    """
    premis_args.pop('eventDate')
    util.createPREMISEventXML(**premis_args)


def test_has_event_element():
    """
    Verify the root element is `event`.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    event = premis.xpath(
        '/p:event',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(event) == 1


def test_eventType_element_text():
    """
    Verify the eventType positional argument yields an eventType
    element with the text from the argument.
    """
    event_type_text = 'Fake Event Type'
    premis = util.createPREMISEventXML(event_type_text, None, None, None)

    eventType = premis.xpath(
        '/p:event/p:eventType',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventType) == 1
    assert eventType[0].text == event_type_text


def test_eventType_element_text_is_none():
    """
    Verify the eventType positional argument yields an eventType
    element with no text.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    eventType = premis.xpath(
        '/p:event/p:eventType',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventType) == 1
    assert eventType[0].text is None


def test_has_eventIdentifier_element():
    """
    Check that the eventIdentifier tree is present.
    """
    premis = util.createPREMISEventXML(None, None, None, None)
    eventIdentifier = premis.xpath(
        '/p:event/p:eventIdentifier',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventIdentifier) == 1
    assert len(eventIdentifier[0].getchildren()) == 2


def test_eventIdentifierValue_element_text():
    """
    Verify the eventIdentifier kwarg yields an eventIdentifier element with
    the text from the argument.
    """
    eventIdentifier = 'ABC'
    premis = util.createPREMISEventXML(None, None, None, None,
                                       eventIdentifier=eventIdentifier)
    eventIdentifierValue = premis.xpath(
        '/p:event/p:eventIdentifier/p:eventIdentifierValue',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventIdentifierValue) == 1
    assert eventIdentifierValue[0].text == eventIdentifier


def test_eventIdentifierValue_element_default_text():
    """
    Verify the eventIdentifier kwarg yields an eventIdentifier element with
    the default text when it is falsy.
    """
    premis = util.createPREMISEventXML(None, None, None, None)
    eventIdentifierValue = premis.xpath(
        '/p:event/p:eventIdentifier/p:eventIdentifierValue',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventIdentifierValue) == 1
    assert eventIdentifierValue[0].text is not None


def test_eventIdentifierType_element_has_text():
    """
    Verify the eventIdentifierType always has text.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    eventIdentifierType = premis.xpath(
        '/p:event/p:eventIdentifier/p:eventIdentifierType',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventIdentifierType) == 1
    assert eventIdentifierType[0].text is not None


def test_eventDateTime_has_default_date():
    """
    Verify the eventDateTime has a datetime when the eventDate kwarg
    is not set.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    eventDateTime = premis.xpath(
        '/p:event/p:eventDateTime',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventDateTime) == 1
    assert eventDateTime[0].text is not None


def test_eventDateTime_element_has_custom_datetime():
    """
    Verify the eventDate kwarg yields an eventDateTime element with
    the text from the argument.
    """
    dt = datetime(2015, 01, 01)
    premis = util.createPREMISEventXML(None, None, None, None, eventDate=dt)
    eventDateTime = premis.xpath(
        '/p:event/p:eventDateTime',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventDateTime) == 1
    assert eventDateTime[0].text == xsDateTime_format(dt)


def test_eventDetail_element_text_is_none():
    """
    Verify the eventDetail text is None when the eventDetail
    positional arg is None.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    eventDetail = premis.xpath(
        '/p:event/p:eventDetail',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventDetail) == 1
    assert eventDetail[0].text is None


def test_eventDetail_element_text():
    """
    Verify the eventDetail positional argument yields an eventDetail
    element with text from the argument.
    """
    details = 'Fake details of the event.'
    premis = util.createPREMISEventXML(None, None, details, None)

    eventDetail = premis.xpath(
        '/p:event/p:eventDetail',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventDetail) == 1
    assert eventDetail[0].text == details


def test_eventOutcome_element_text_is_none():
    """
    Verify the eventOutcome positional argument yields an empty
    eventOutcome element when the argument is None.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    eventOutcome = premis.xpath(
        '/p:event/p:eventOutcomeInformation/p:eventOutcome',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventOutcome) == 1
    assert eventOutcome[0].text is None


def test_eventOutcome_element_text():
    """
    Verify the eventOutcome positional argument yields an eventOutcome
    element with text from the argument.
    """
    outcome = 'Fake event outcome.'
    premis = util.createPREMISEventXML(None, None, None, outcome)

    eventOutcome = premis.xpath(
        '/p:event/p:eventOutcomeInformation/p:eventOutcome',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventOutcome) == 1
    assert eventOutcome[0].text == outcome


def test_has_no_eventOutcomeDetail_element():
    """
    Check that the eventOutcomeDetail element is not created when
    an eventOutcome is present but the outcomeDetail kwarg is not.
    """
    outcome = 'Fake event outcome.'
    premis = util.createPREMISEventXML(None, None, None, outcome)

    eventOutcomeDetail = premis.xpath(
        '/p:event/p:eventOutcomeInformation/p:eventOutcomeDetail',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventOutcomeDetail) == 0


def test_eventOutcomeDetail_element_text():
    """
    Verify the outcomeDetail kwarg yields an eventOutcomeDetail
    element with text from the argument.
    """
    outcomeDetail = 'Fake event outcome details.'
    premis = util.createPREMISEventXML(None, None, None, None,
                                       outcomeDetail=outcomeDetail)
    eventOutcomeDetailNote = premis.xpath(
        '/p:event/p:eventOutcomeInformation/p:eventOutcomeDetail/' +
        'p:eventOutcomeDetailNote',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(eventOutcomeDetailNote) == 1
    assert eventOutcomeDetailNote[0].text == outcomeDetail


def test_linkingAgentIdentifierType_element_text():
    """
    Verify the linkingAgentIdentifierType text is present.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    linkingAgentIdentifierType = premis.xpath(
        '/p:event/p:linkingAgentIdentifier/p:linkingAgentIdentifierType',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingAgentIdentifierType) == 1
    assert linkingAgentIdentifierType[0].text is not None


def test_linkingAgentIdentifierRole_element_text():
    """
    Verify the linkingAgentIdentifierRole text is present.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    linkingAgentIdentifierRole = premis.xpath(
        '/p:event/p:linkingAgentIdentifier/p:linkingAgentRole',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingAgentIdentifierRole) == 1
    assert linkingAgentIdentifierRole[0].text is not None


def test_linkingAgentIdentifierValue_element_text_is_none():
    """
    Verify the agentIdentifier positional argument yields a
    linkingAgentIdentifierValue element with no text when the
    argument is None.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    linkingAgentIdentifierValue = premis.xpath(
        '/p:event/p:linkingAgentIdentifier/p:linkingAgentIdentifierValue',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingAgentIdentifierValue) == 1
    assert linkingAgentIdentifierValue[0].text is None


def test_linkingAgentIdentifierValue_element_text():
    """
    Verify the agentIdentifier positional argument yields a
    linkingAgentIdentifierValue element with text from the argument.
    """
    agent = 'John Doe'
    premis = util.createPREMISEventXML(None, agent, None, None)

    linkingAgentIdentifierValue = premis.xpath(
        '/p:event/p:linkingAgentIdentifier/p:linkingAgentIdentifierValue',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingAgentIdentifierValue) == 1
    assert linkingAgentIdentifierValue[0].text == agent


def test_has_no_linkingObjectIdentifier_element():
    """
    Check that the linkingObjectIdentifier is not present when
    the objectList kwarg uses the default value.
    """
    premis = util.createPREMISEventXML(None, None, None, None)

    linkingObjectIdentifier = premis.xpath(
        '/p:event/p:linkingObjectIdentifier',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingObjectIdentifier) == 0


def test_linkingObjectIdentifierType_element_text():
    """
    Verify the linkObjectList kwarg yields a linkingObjectIdentifierType
    element with the value being the second element of the identifier
    tuple.
    """
    identifier = (
        '000-000',
        'http://example.com/object',
        'fake object'
    )
    premis = util.createPREMISEventXML(None, None, None, None,
                                       linkObjectList=[identifier])

    linkingObjectIdentifierType = premis.xpath(
        '/p:event/p:linkingObjectIdentifier/p:linkingObjectIdentifierType',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingObjectIdentifierType) == 1
    assert linkingObjectIdentifierType[0].text == identifier[1]


def test_linkingObjectIdentifierValue_element_text():
    """
    Verify the linkObjectList kwarg yields a linkingObjectIdentifierValue
    element with the value being the first element of the identifier
    tuple.
    """
    identifier = (
        '000-000',
        'http://example.com/object',
        'fake object'
    )
    premis = util.createPREMISEventXML(None, None, None, None,
                                       linkObjectList=[identifier])

    linkingObjectIdentifierValue = premis.xpath(
        '/p:event/p:linkingObjectIdentifier/p:linkingObjectIdentifierValue',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingObjectIdentifierValue) == 1
    assert linkingObjectIdentifierValue[0].text == identifier[0]


def test_linkingObjectRole_element_text():
    """
    Verify the linkObjectList kwarg yields a linkingObjectRole
    element with the value being the last element of the identifier
    tuple.
    """
    identifier = (
        '000-000',
        'http://example.com/object',
        'fake object'
    )
    premis = util.createPREMISEventXML(None, None, None, None,
                                       linkObjectList=[identifier])

    linkingObjectRole = premis.xpath(
        '/p:event/p:linkingObjectIdentifier/p:linkingObjectRole',
        namespaces={'p': util.PREMIS_NAMESPACE}
    )
    assert len(linkingObjectRole) == 1
    assert linkingObjectRole[0].text == identifier[2]


@pytest.mark.parametrize('object_list', [
    [('a', 'b', 'c', 'd'), ('e', 'f', 'g', 'h')],
    [('a', 'b', 'c'), ('d', 'e', 'f')],
    pytest.mark.xfail([('a', 'b'), ('c', 'd')]),
    pytest.mark.xfail([('a',), ('b',)]),
    pytest.mark.xfail([(), ()])
])
def test_linkObjectList_handles_any_size_tuple(object_list, premis_args):
    """
    Test to verify that various sized identifier tuples can be handled
    when pass via the linkObjectList kwarg.

    If unsuccessful, a exception will bubble up and cause a failure.
    """
    premis_args.update(linkObjectList=object_list)
    util.createPREMISEventXML(**premis_args)
