from datetime import datetime

from lxml import etree
import pytest

from codalib import bagatom


class NodeStub(object):
    """
    Test stub that implements the Node model interface.
    """
    node_name = 'Test Name'
    node_url = 'http://example.com/node'
    node_path = '/foo/bar/node'
    node_capacity = 4096
    node_size = 2048
    last_checked = datetime(2015, 01, 01)


def test_return_type():
    """
    Verify the return type of nodeToXML is an instance of
    etree._Element.
    """
    tree = bagatom.nodeToXML(NodeStub())
    assert isinstance(tree, etree._Element)


@pytest.mark.parametrize('element,text', [
    ('name', 'Test Name'),
    ('url', 'http://example.com/node'),
    ('path', '/foo/bar/node'),
    ('capacity', '4096'),
    ('size', '2048'),
    ('lastChecked', '2015-01-01T00:00:00Z'),
])
def test_has_element(element, text):
    """
    Check that the returned tree has various elements.
    """
    node_xml = bagatom.nodeToXML(NodeStub())
    element = node_xml[0].xpath(
        '/n:node/n:{0}'.format(element),
        namespaces={'n': bagatom.NODE_NAMESPACE}
    )
    assert len(element) == 1
    assert element[0].text == text


def test_does_not_have_lastChecked():
    """
    Verify that the returned tree does not have the lastChecked
    element.
    """
    node = NodeStub()
    node.last_checked = None

    node_xml = bagatom.nodeToXML(node)

    element = node_xml[0].xpath(
        '/n:node/n:lastChecked',
        namespaces={'n': bagatom.NODE_NAMESPACE}
    )
    assert len(element) == 0
