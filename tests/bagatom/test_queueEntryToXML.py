from datetime import datetime

from lxml import etree
import pytest

from codalib import bagatom


@pytest.fixture(scope='module')
def queue_stub():
    class QueueStub(object):
        ark = 'ark:65443'
        oxum = '1394.7'
        url_list = 'http://example.com.urls'
        status = 'Completed'
        harvest_start = '2013-05-17T01:12:20Z'
        harvest_end = '2013-05-17T01:12:33Z'
        queue_position = 5

    return QueueStub()


def test_return_value(queue_stub):
    """
    Verify the return type is an instance of etree._Element.
    """
    tree = bagatom.queueEntryToXML(queue_stub)
    assert isinstance(tree, etree._Element)


def test_root_node(queue_stub):
    """
    Verify the root element of the return tree is queueEntry.
    """
    xml = bagatom.queueEntryToXML(queue_stub)

    root = xml.xpath(
        '/q:queueEntry',
        namespaces={'q': bagatom.QXML_NAMESPACE}
    )
    assert len(root) == 1


@pytest.mark.parametrize('name,attr', [
    ('ark', 'ark'),
    ('oxum', 'oxum'),
    ('urlListLink', 'url_list'),
    ('status', 'status'),
    ('position', 'queue_position'),
    ('start', 'harvest_start'),
    ('end', 'harvest_end')
])
def test_has_element(name, attr, queue_stub):
    """
    Check that various elements are present and have the expected text.

    The `name` parameter is the element name, and the `attr` parameter is
    the name of the attribute on the QueueStub fixture.
    """
    xml = bagatom.queueEntryToXML(queue_stub)

    element = xml.xpath(
        '/q:queueEntry/q:{0}'.format(name),
        namespaces={'q': bagatom.QXML_NAMESPACE}
    )
    expected = getattr(queue_stub, attr)

    assert len(element) == 1
    assert element[0].text == str(expected)


def test_queue_has_datetime_harvest_start(queue_stub):
    """
    Check that queueEntryToXML accepts a datetime object in the
    harvest_start property.
    """
    queue_stub.harvest_start = datetime(2015, 1, 1, 0, 0, 0)

    xml = bagatom.queueEntryToXML(queue_stub)
    start = xml.xpath(
        '/q:queueEntry/q:start',
        namespaces={'q': bagatom.QXML_NAMESPACE}
    )
    assert len(start) == 1
    assert start[0].text == queue_stub.harvest_start.strftime(
        bagatom.TIME_FORMAT_STRING)


def test_queue_has_datetime_harvest_end(queue_stub):
    """
    Check that queueEntryToXML accepts a datetime object in the
    harvest_end property.
    """
    queue_stub.harvest_end = datetime(2015, 1, 1, 0, 0, 0)

    xml = bagatom.queueEntryToXML(queue_stub)
    end = xml.xpath(
        '/q:queueEntry/q:end',
        namespaces={'q': bagatom.QXML_NAMESPACE}
    )
    assert len(end) == 1
    assert end[0].text == queue_stub.harvest_end.strftime(
        bagatom.TIME_FORMAT_STRING)


def test_queue_empty_start_end(queue_stub):
    """
    Check that empty start/end values are omitted in QueueXML
    """

    queue_stub.harvest_start = None
    queue_stub.harvest_end = None

    xml = bagatom.queueEntryToXML(queue_stub)
    end = xml.xpath(
        '/q:queueEntry/q:end',
        namespaces={'q': bagatom.QXML_NAMESPACE}
    )
    start = xml.xpath(
        '/q:queueEntry/q:start',
        namespaces={'q': bagatom.QXML_NAMESPACE}
    )
    assert len(end) == 0
    assert len(start) == 0
