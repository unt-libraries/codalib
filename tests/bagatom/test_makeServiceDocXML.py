from lxml import etree

from codalib import bagatom


def test_return_type():
    """
    Check that return value is an instance of etree._Element.
    """
    c = dict(
        title='Collection C',
        href='http://example.com/collection/c',
        accept='no')

    xml = bagatom.makeServiceDocXML('Test Type', [c])
    assert isinstance(xml, etree._Element)


def test_can_handle_empty_collections_list():
    """
    Check that an empty list can be passed to makeServiceDocXML.
    """
    xml = bagatom.makeServiceDocXML('Test Type', [])
    assert isinstance(xml, etree._Element)


def test_has_service_element():
    """
    Check the service element is present in the returned tree.
    """
    xml = bagatom.makeServiceDocXML('Test Title', [])
    service = xml[0].xpath('/service')
    assert len(service) == 1
    assert service[0].tag == 'service'


def test_has_workspace_element():
    """
    Check the workspace element is present in the returned tree.
    """
    xml = bagatom.makeServiceDocXML('Test Title', [])
    workspace = xml[0].xpath('/service/workspace')
    assert len(workspace) == 1
    assert workspace[0].tag == 'workspace'


def test_has_title_element():
    """
    Check the title element is present in the returned tree and
    includes the text from the title positional argument.
    """
    xml = bagatom.makeServiceDocXML('Test Title', [])
    title = xml[0].xpath(
        '/service/workspace/n:title',
        namespaces={'n': bagatom.ATOM_NAMESPACE}
    )
    assert len(title) == 1
    assert title[0].text == 'Test Title'


def test_has_collection_element():
    """
    Check the collection element is present in the returned tree.
    """
    c = dict(
        title='Collection A',
        href='http://example.com/collection/a',
        accept='yes')

    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection = xml[0].xpath('/service/workspace/collection')
    assert len(collection) == 1
    assert collection[0].tag == 'collection'
    assert len(collection[0].getchildren()) == 2


def test_has_collection_elements():
    """
    Verify the collection child elements are present.
    """
    c = dict(
        title='Collection A',
        href='http://example.com/collection/a',
        accept='yes')

    # Dummy list of collections.
    collections = [c, c, c, c]
    xml = bagatom.makeServiceDocXML('Test Title', collections)
    collection_element = xml[0].xpath('/service/workspace/collection')
    assert len(collection_element) == len(collections)


def test_has_no_collection_element():
    """
    Verify the returned tree has no collection elements when no
    collection dictionaries are passed in.
    """
    xml = bagatom.makeServiceDocXML('Test Title', [])
    collection_element = xml[0].xpath('/service/workspace/collection')
    assert len(collection_element) == 0


def test_collection_element_has_href():
    """
    Verify the collection element uses the href item from the
    collection dictionary.
    """
    c = dict(href='http://example.com/collection/a')

    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection = xml[0].xpath('/service/workspace/collection')
    assert collection[0].attrib.get('href') == c['href']


def test_collection_element_does_not_have_href():
    """
    Verify the collection element does not have an href attribute.
    """
    c = dict(title='Collection Title')

    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection = xml[0].xpath('/service/workspace/collection')
    assert collection[0].attrib.get('href') is None


def test_has_collection_title_element():
    """
    Verify the collection element uses the title item from the
    collection dictionary.
    """
    c = dict(title='Collection Title')

    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection_title = xml[0].xpath(
        '/service/workspace/collection/n:title',
        namespaces={'n': bagatom.ATOM_NAMESPACE})

    assert len(collection_title) == 1
    assert collection_title[0].text == c['title']


def test_does_not_have_collection_title_element():
    """
    Verify the collection element does not have a title element.
    """
    c = dict(accept='all')

    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection_title = xml[0].xpath(
        '/service/workspace/collection/n:title',
        namespaces={'n': bagatom.ATOM_NAMESPACE})

    assert len(collection_title) == 0


def test_has_collection_accept_element():
    """
    Verify the collection element uses the accept item from the
    collection dictionary.
    """
    c = dict(accept='all')
    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection_accept = xml[0].xpath('/service/workspace/collection/accept')
    assert len(collection_accept) == 1
    assert collection_accept[0].text == c['accept']
    assert collection_accept[0].tag == 'accept'


def test_does_not_have_collection_accept_element():
    """
    Verify the collection element does not have an accept element.
    """
    c = dict(title='Collection Title')
    xml = bagatom.makeServiceDocXML('Test Title', [c])
    collection_accept = xml[0].xpath('/service/workspace/collection/accept')
    assert len(collection_accept) == 0
