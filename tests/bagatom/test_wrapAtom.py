from datetime import datetime

from lxml import etree

from codalib import bagatom
from codalib.xsdatetime import xsDateTime_parse


xml = """<note>
            <to>Tove</to>
            <from>Jani</from>
            <heading>Reminder</heading>
            <body>Don't forget me this weekend!</body>
        </note>
"""


def test_return_type():
    """
    Verify the return type of wrapAtom is an instance of etree._Element.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test')
    assert isinstance(atom, etree._Element)


def test_has_date():
    """
    Check the returned tree has an updated element by default.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test')

    updated = atom.xpath(
        '/a:entry/a:updated',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(updated) == 1


def test_uses_date():
    """
    Check the returned tree uses the `updated` kwarg text for the
    updated element.
    """
    updated = datetime(2012, 12, 12)

    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test', updated=updated)

    elements = atom.xpath(
        '/a:entry/a:updated',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(elements) == 1

    date = xsDateTime_parse(elements[0].text)
    assert date == updated


def test_has_title():
    """
    Check that the title element is present.
    """
    title = 'Test Title'

    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', title)

    elements = atom.xpath(
        '/a:entry/a:title',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(elements) == 1
    assert elements[0].text == title


def test_has_id():
    """
    Check that the id element is present.
    """
    title = 'Test Title'
    _id = '2910'

    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, _id, title)

    elements = atom.xpath(
        '/a:entry/a:id',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(elements) == 1
    assert elements[0].text == _id


def test_has_content():
    """
    Check that the content element is present and has a type
    attribute of `application/xml`.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test')

    content = atom.xpath(
        '/a:entry/a:content',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(content) == 1

    attributes = content[0].attrib
    assert attributes.get('type') == 'application/xml'


def test_has_author_name():
    """
    Verify the author element is present.
    """
    author_text = 'John Doe'
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test', author=author_text)

    author = atom.xpath(
        '/a:entry/a:author/a:name',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(author) == 1
    assert author[0].text == author_text


def test_has_no_author():
    """
    Verify the author element is not present if the author kwarg is not
    specified.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test')

    author = atom.xpath(
        '/a:entry/a:author',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(author) == 0


def test_has_author_uri():
    """
    Verify the author_uri is present.
    """
    author_uri_text = 'http://example.com/author'
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test', author_uri=author_uri_text)

    author_uri = atom.xpath(
        '/a:entry/a:author/a:uri',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(author_uri) == 1
    assert author_uri[0].text == author_uri_text


def test_has_no_author_uri():
    """
    Verify the author_url element is not present if the
    author_uri_text kwarg is not set.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test')

    author_uri = atom.xpath(
        '/a:entry/a:author/a:uri',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(author_uri) == 0


def test_has_author_and_author_uri():
    """
    Verify that both the author and author_uri are present if both
    kwargs are given values.
    """
    author_text = 'John Doe'
    author_uri_text = 'http://example.com/author'
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test', author=author_text,
                            author_uri=author_uri_text)

    author = atom.xpath(
        '/a:entry/a:author',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert len(author[0].getchildren()) == 2


def test_content_is_preserved():
    """
    Verify that the content is preserved after it has been wrapped.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test')

    content = atom.xpath(
        '/a:entry/a:content',
        namespaces={'a': bagatom.ATOM_NAMESPACE}
    )
    assert xml.strip() in etree.tostring(content[0])


def test_has_alternate_relationship_link():
    """
    Verify the entry has an alternate link.
    """
    root = etree.fromstring(xml)
    atom = bagatom.wrapAtom(root, '934023', 'test', alt='http://example.com')

    link = atom.xpath(
        "/a:entry/a:link[@rel='alternate']",
        namespaces={'a': bagatom.ATOM_NAMESPACE})

    assert link[0].get('href') == 'http://example.com'
