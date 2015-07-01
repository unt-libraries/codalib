import os

from mock import mock_open
import pytest

from codalib import bagatom


# Settings for the monkeypatched fixtures
TEST_NAME = 'baz'
TEST_PATH = os.path.join('/foo/bar', TEST_NAME)
FILE_COUNT = 3
PAYLOAD_SIZE = 1500
BAGGING_DATE = '2015-01-01'
BAGIT_CONTENTS = 'BagIt-Version: 0.96\nTag-File-Character-Encoding: UTF-8'


@pytest.fixture
def bagxml(monkeypatch):
    """
    Test fixture that patches the following functions.
        open()
        bagatom.getBagTags()
        bagatom.getOxum()
    """
    m = mock_open(read_data=BAGIT_CONTENTS)
    monkeypatch.setattr('__builtin__.open', m)

    monkeypatch.setattr('codalib.bagatom.getBagTags', lambda x: {})

    monkeypatch.setattr(
        'codalib.bagatom.getOxum',
        lambda x: '{0}.{1}'.format(PAYLOAD_SIZE, FILE_COUNT)
    )

    return bagatom.bagToXML(TEST_PATH)


@pytest.fixture
def bagxml_with_tags(monkeypatch):
    """
    Test fixture that patches the following functions:
        open()
        bagatom.getBagTags()
        bagatom.getOxum()

    Returns a predefined set of tags.
    """
    m = mock_open(read_data=BAGIT_CONTENTS)
    monkeypatch.setattr('__builtin__.open', m)

    bagtags = {
        'Source-Organization': 'Test Org',
        'Bag-Size': '1GB'
    }
    monkeypatch.setattr('codalib.bagatom.getBagTags', lambda x: bagtags)

    monkeypatch.setattr(
        'codalib.bagatom.getOxum',
        lambda x: '{0}.{1}'.format(PAYLOAD_SIZE, FILE_COUNT)
    )

    return bagatom.bagToXML(TEST_PATH)


@pytest.fixture
def bagxml_with_bagging_date(monkeypatch):
    """
    Test fixture that patches the following functions:
        open()
        bagatom.getBagTags()
        bagatom.getOxum()

    Returns a predefined set of tags, including the
    Bagging-Date tag.
    """
    m = mock_open(read_data=BAGIT_CONTENTS)
    monkeypatch.setattr('__builtin__.open', m)

    bagtags = {
        'Payload-Oxum': '{0}.{1}'.format(PAYLOAD_SIZE, FILE_COUNT),
        'Bagging-Date': BAGGING_DATE
    }
    monkeypatch.setattr('codalib.bagatom.getBagTags', lambda x: bagtags)
    return bagatom.bagToXML(TEST_PATH)


def test_returns_tree(bagxml):
    """
    Check the type of the value returned by bagToXML.
    """
    name = bagxml[0].xpath(
        '/a:codaXML/a:name',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(name) == 1
    assert name[0].text == 'ark:/67531/{0}'.format(TEST_NAME)


def test_return_tree_has_fileCount(bagxml):
    """
    Verify the return value has a fileCount element.
    """
    fileCount = bagxml[0].xpath(
        '/a:codaXML/a:fileCount',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(fileCount) == 1
    assert fileCount[0].text == str(FILE_COUNT)


def test_return_tree_has_payloadSize(bagxml):
    """
    Verify the return value has a payloadSize element.
    """
    payloadSize = bagxml[0].xpath(
        '/a:codaXML/a:payloadSize',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(payloadSize) == 1
    assert payloadSize[0].text == str(PAYLOAD_SIZE)


def test_return_tree_has_bagitVersion(bagxml):
    """
    Verify the return value has a bagitVersion element.
    """
    bagitVersion = bagxml[0].xpath(
        '/a:codaXML/a:bagitVersion',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(bagitVersion) == 1
    assert bagitVersion[0].text == '0.96'


def test_return_tree_has_lastVerified(bagxml):
    """
    Verify the return value has a lastVerified element.
    """
    lastVerified = bagxml[0].xpath(
        '/a:codaXML/a:lastVerified',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(lastVerified) == 1
    assert lastVerified[0].text is None


def test_return_tree_has_lastStatus(bagxml):
    """
    Verify the return value has a lastStatus element.
    """
    lastStatus = bagxml[0].xpath(
        '/a:codaXML/a:lastStatus',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(lastStatus) == 1
    assert lastStatus[0].text is None


def test_return_tree_has_bagInfo(bagxml):
    """
    Verify the return value has a bagInfo element.
    """
    bagInfo = bagxml[0].xpath(
        '/a:codaXML/a:bagInfo',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(bagInfo) == 1
    assert len(bagInfo[0].getchildren()) == 1


def test_return_tree_check_item_children(bagxml_with_tags):
    """
    Verify the return value has the correct item child elements
    and values.
    """
    # Get all the item values and put them into a list.
    items = bagxml_with_tags[0].xpath(
        '/a:codaXML/a:bagInfo/a:item//text()',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )

    assert 'Bag-Size' in items
    assert '1GB' in items
    assert 'Payload-Oxum' in items
    assert '1500.3' in items
    assert 'Source-Organization' in items
    assert 'Test Org' in items


def test_return_tree_has_no_baggingDate(bagxml):
    """
    Verify the return value does not have a baggingDate element.
    """
    baggingDate = bagxml[0].xpath(
        '/a:codaXML/a:baggingDate',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert len(baggingDate) == 0


def test_return_tree_with_baggingDate(bagxml_with_bagging_date):
    """
    Check that the return tree baggingDate element value is correct.
    """
    baggingDate = bagxml_with_bagging_date[0].xpath(
        '/a:codaXML/a:baggingDate',
        namespaces={'a': bagatom.BAG_NAMESPACE}
    )
    assert baggingDate[0].text == BAGGING_DATE
