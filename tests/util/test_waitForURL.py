from time import sleep
from unittest.mock import MagicMock
import http.client
import urllib.error

from codalib.util import waitForURL


def test_url_call_succeeds_with_200(monkeypatch):
    """
    Test the function will return once the HTTP Response is
    200 OK.
    """
    # Setup the mocks.
    response = MagicMock(spec=http.client.HTTPResponse)
    response.getcode.return_value = 200
    mock_urlopen = MagicMock(return_value=response)

    # Path urlopen so that we do not make an http request.
    monkeypatch.setattr('urllib.request.urlopen', mock_urlopen)

    waitForURL('http://exmple.com/foo/bar')

    assert mock_urlopen.call_count == 1
    assert response.getcode.called


def test_excepts_URLError(monkeypatch):
    """
    Check that the function can handle urllib.request.URLErrors and
    immediately retry.
    """
    response = MagicMock(spec=http.client.HTTPResponse)
    response.getcode.return_value = 200

    side_effects = [urllib.error.URLError('Mock Exception'), response]
    mock_urlopen = MagicMock(side_effect=side_effects)

    # Patch sleep to decrease the amount of time between each
    # iteration in waitForURL.
    monkeypatch.setattr('urllib.request.urlopen', mock_urlopen)
    monkeypatch.setattr('time.sleep', lambda x: sleep(.01))

    waitForURL('http://exmple.com/foo/bar')
    assert mock_urlopen.call_count == 2
    assert response.getcode.called


def test_url_response_fails(monkeypatch):
    """
    Verify the function will return if the HTTP Request
    continues to fail.
    """
    response = MagicMock(spec=None)
    mock_urlopen = MagicMock(return_value=response)

    monkeypatch.setattr('urllib.request.urlopen', mock_urlopen)
    monkeypatch.setattr('time.sleep', lambda x: sleep(1))

    # Set the max_seconds to less than the sleep time so the
    # while loop will terminate on the second iteration.
    waitForURL('http://exmple.com/foo/bar', max_seconds=.01)
    assert not response.getcode.called
    assert mock_urlopen.call_count == 2
