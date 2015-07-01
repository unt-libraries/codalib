import os

from lxml import etree
from mock import mock_open
import pytest

from codalib import bagatom


def test_getOxum(monkeypatch):
    """
    Check the return value of getOxum with patched system calls.

    getOxum should return the total size and the total number
    of files in the directory in the form of
    `<total size>.<total files>`
    """

    def walk(thin):
        """Stub for os.walk."""
        return [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs'))
        ]

    class MockStat(object):
        """Stub for os.stat."""
        st_size = 500

        def __init__(self, *args):
            pass

    monkeypatch.setattr(os, 'walk', walk)
    monkeypatch.setattr(os, 'stat', MockStat)

    assert bagatom.getOxum('') == "1500.3"


@pytest.fixture(scope='module')
def note_xml():
    return """<note xmlns="http://example.com/namespace">
                  <to>Tove</to>
                  <from>
                    <name>Jani</name>
                    <email>jani@example.com</email>
                  </from>
                  <heading>Reminder</heading>
                  <body>Don't forget me this weekend!</body>
              </note>
    """


@pytest.fixture(scope='module')
def people_xml():
    return """<people xmlns="http://example.com/namespace">
                  <name>Tove</name>
                  <name>Jani</name>
                  <nickname>Junior</nickname>
              </people>
    """


def test_getBagTags_returns_dict(monkeypatch):
    """
    Check the return value of getBagTags.
    """
    # Patch the builtin function `open` with the mock_open
    # function.
    m = mock_open(read_data='tag: tag')
    monkeypatch.setattr('__builtin__.open', m)

    tags = bagatom.getBagTags('.')
    assert tags == {'tag': 'tag'}


def test_getBagTags_open_decodes_utf8(monkeypatch):
    """
    Check that getBagTags decodes the file contents from UTF-8.

    To verify this, we assert that the mock was only called once.
    """
    m = mock_open(read_data='tag: tag')
    monkeypatch.setattr('__builtin__.open', m)
    bagatom.getBagTags('.')
    assert m.call_count == 1


def test_getBagTags_open_decodes_iso8859_1(monkeypatch):
    """
    Check that getBagTags decodes the file contents from ISO-8859-1.

    To verify this, we assert that the mock was called twice. The first
    attempt trying to decode UTF-8, then retrying with ISO-8859-1.
    """
    m = mock_open(read_data='tag: \x81')
    monkeypatch.setattr('__builtin__.open', m)
    tags = bagatom.getBagTags('.')

    assert m.call_count == 2
    assert tags == {'tag': u'\x81'}


def test_getValueByName_returns_value(note_xml):
    """
    Check that getValueByName returns the correct value.
    """
    root = etree.fromstring(note_xml)
    value = bagatom.getValueByName(root, 'to')
    assert value == 'Tove'


def test_getValueByName_returns_None(note_xml):
    """
    Verify getValueByName returns None when the desired element does
    not exist in the tree.
    """
    root = etree.fromstring(note_xml)
    value = bagatom.getValueByName(root, 'entry')
    assert value is None


def test_getNodeByName_returns_node(note_xml):
    """
    Check that getNodeByName returns an etree._Element and that
    the returned element matches the root child element.
    """
    root = etree.fromstring(note_xml)
    to_node = root.getchildren()[0]
    node = bagatom.getNodeByName(root, 'to')

    assert isinstance(node, etree._Element)
    assert node is to_node


def test_getNodeByName_returns_None(note_xml):
    """
    Verify getNodeByName returns None when the desired element does
    not exist in the tree.
    """
    root = etree.fromstring(note_xml)
    node = bagatom.getNodeByName(root, 'entry')
    assert node is None


def test_getNodeByName_raises_exception_without_node_param():
    """
    Check that an exception is raised if the node is not passed
    to the function.
    """
    with pytest.raises(Exception) as e:
        bagatom.getNodeByName(None, 'element')

    assert 'Cannot search for a child' in str(e.value)


def test_getNodeByName_raises_exception_without_name_param():
    """
    Check that an exception is raised if the element name is not
    passed to the function.
    """
    with pytest.raises(Exception) as e:
        bagatom.getNodeByName('node', None)

    assert 'Unspecified name to find node for.' == str(e.value)


def test_getNodesByName_returns_list(people_xml):
    """
    Check that the two nodes with the element `name` are
    in the returned list.
    """
    root = etree.fromstring(people_xml)
    names = root.getchildren()[:2]
    nodes = bagatom.getNodesByName(root, 'name')

    assert len(nodes) == 2
    assert nodes == names


def test_getNodesByName_returns_empty_list(people_xml):
    """
    Verify that no nodes are in the list if the tree does not contain
    the element that was queried for.
    """
    root = etree.fromstring(people_xml)
    nodes = bagatom.getNodesByName(root, 'age')
    assert len(nodes) == 0


def test_getNodeByNameChain_returns_correct_node(note_xml):
    """
    Check that getNodeByNameChain returns the correct node.
    """
    root = etree.fromstring(note_xml)
    chain = ['from', 'name']
    node = bagatom.getNodeByNameChain(root, chain)
    assert node.text == 'Jani'


def test_getNodeByNameChain_raises_exception(note_xml):
    """
    Verify that getNodeByNameChain raises an exception if the
    path specified in the chain does not exist in the XML tree.
    """
    root = etree.fromstring(note_xml)
    # This chain is invalid because the `to` element does not
    # have any children.
    chain = ['to', 'cc']

    with pytest.raises(Exception):
        bagatom.getNodeByNameChain(root, chain)


def test_getNodeByNameChain_returns_same_node_with_empty_chain_list(note_xml):
    """
    Test that the passed in tree is returned unchanged if the chain_list
    positional argument is an empty list.
    """
    root = etree.fromstring(note_xml)
    node = bagatom.getNodeByNameChain(root, [])
    assert node == root
