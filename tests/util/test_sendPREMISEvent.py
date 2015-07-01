from urllib2 import URLError

from mock import Mock
import pytest

from codalib import util


def test_is_successful(monkeypatch):
    """
    Check that sendPremisEvent returns the response and content.

    Verify the conditions will cause no exceptions to be
    raised or caught.
    """
    response = Mock(code=201)

    expected = (response, 'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    actual = util.sendPREMISEvent(
        'http://example.com', None, None, None, None)

    assert doWebRequest.call_count == 1
    assert actual == expected


def test_raises_exception_when_doWebRequest_fails(monkeypatch):
    """
    Check that sendPremisEvent raises an exception when the HTTP
    request is unable to yield a response repeatedly.
    """
    waitForURL = Mock()

    doWebRequest = Mock(side_effect=URLError('Fake Error'))

    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)
    monkeypatch.setattr('codalib.util.waitForURL', waitForURL)

    with pytest.raises(URLError):
        util.sendPREMISEvent('http://example.com', None, None, None, None)

    assert doWebRequest.call_count == 2


def test_raises_exception_without_201_status(monkeypatch):
    """
    Verify that sendPREMISEvent will raise an exception when the
    returned response does not have a status code 201.
    """
    response = Mock(code=200)

    expected = (response, 'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    with pytest.raises(Exception):
        util.sendPREMISEvent('http://example.com', None, None, None, None)

    assert doWebRequest.call_count == 1
