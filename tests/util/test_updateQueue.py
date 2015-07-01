from urllib2 import URLError

from mock import Mock
import pytest

from codalib import util


@pytest.fixture
def queue_dict():
    """
    Fixture to provide a valid queue dictionary as required by
    updateQueue.

    updateQueue expects all of the keys below to be present.
    """
    return {
        'ark': 'fake ark',
        'oxum': 'fake oxum',
        'url_list': 'fake url list',
        'status': 'fake status',
        'queue_position': 'fake queue position'
    }


def test_request_is_successful(queue_dict, monkeypatch):
    """
    Check that updateQueue will make a single call to doWebRequest
    and return under the correct conditions.
    """
    response = Mock()
    response.getcode.return_value = 200

    expected = (response, 'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    util.updateQueue('/foo/bar', queue_dict)

    assert response.getcode.call_count == 1
    assert doWebRequest.call_count == 1


def test_raises_exception_with_200_status(queue_dict, monkeypatch):
    """
    Check that updateQueue will raise an Exception if the response
    returned from doWebRequest does not have status code 200.
    """
    response = Mock()
    response.getcode.return_value = 201

    expected = (response, 'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    with pytest.raises(Exception):
        util.updateQueue('/foo/bar', queue_dict)

    assert doWebRequest.call_count == 1


def test_fails_second_request_attempt(queue_dict, monkeypatch):
    """
    Verify that an exception will bubble up if the second call to
    doWebRequest fails and raises a urllib2.URLError.
    """
    doWebRequest = Mock(side_effect=URLError('Fake Exception'))
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)
    monkeypatch.setattr('time.sleep', lambda x: True)

    with pytest.raises(URLError):
        util.updateQueue('/foo/bar', queue_dict)

    assert doWebRequest.call_count == 2


def test_second_request_attempt_succeeds(queue_dict, monkeypatch):
    """
    Check that updateQueue will return after the second call to
    doWebRequest is successful.
    """
    response = Mock()
    response.getcode.return_value = 200

    side_effect = [
        URLError('Fake Exception'),
        (response, 'Fake content')
    ]
    doWebRequest = Mock(side_effect=side_effect)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)
    monkeypatch.setattr('time.sleep', lambda x: True)

    util.updateQueue('/foo/bar', queue_dict)

    assert response.getcode.call_count == 1
    assert doWebRequest.call_count == 2
