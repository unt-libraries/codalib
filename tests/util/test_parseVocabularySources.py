import json

from mock import mock_open, patch
import pytest

from codalib import util


def test_return_value():
    """
    Test that parseVocabularySources returns a list of the correct length
    where all elements are tuples.
    """
    read_data = json.dumps({
        'terms': [
            {'name': 'foo', 'label': 'Foo'},
            {'name': 'bar', 'label': 'Bar'},
            {'name': 'baz', 'label': 'Baz'},
            {'name': 'qux', 'label': 'Qux'}
        ]
    })

    m = mock_open(read_data=read_data)
    with patch('codalib.util.open', m):
        choices = util.parseVocabularySources('/foo/bar')

    assert len(choices) == 4
    # Verify that all elements of the list are tuples.
    assert all([type(choice) is tuple for choice in choices])


def test_return_value_elements():
    """
    Verify that the returned list elements contain the name and the label.
    """
    read_data = json.dumps({
        'terms': [
            {'name': 'foo', 'label': 'Foo'}
        ]
    })

    m = mock_open(read_data=read_data)
    with patch('codalib.util.open', m):
        choices = util.parseVocabularySources('/foo/bar')
    assert choices.pop() == ('foo', 'Foo')


@pytest.mark.xfail
def test_empty_file_does_not_raise_exception():
    """
    Verify that an exception will not be raised if the file is empty.
    """
    m = mock_open()
    with patch('codalib.util.open', m):
        util.parseVocabularySources('/foo/bar')


@pytest.mark.xfail
def test_empty_json_does_not_raise_exception():
    """
    Verify that an exception will not be raised if the file has a json
    object, but the object is empty.
    """
    read_data = json.dumps({})
    m = mock_open(read_data=read_data)
    with patch('codalib.util.open', m):
        util.parseVocabularySources('/foo/bar')
