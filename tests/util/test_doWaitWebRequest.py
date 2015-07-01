from urllib2 import URLError

from mock import Mock

from codalib import util


def test_is_sucessful(monkeypatch):
    """
    Verifies the return value from a successful call to
    doWaitWebRequest.
    """
    response = Mock()
    doWebRequest = Mock(return_value=(response, 'fake content'))

    # Patch doWebRequest so that we do not make an http request.
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)
    url = 'http://example.com/foo/bar'
    return_value = util.doWaitWebRequest(url)
    assert return_value == (response, 'fake content')


def test_retries_request(monkeypatch):
    """
    Check that the request is attempted again if a URLError is raised.
    """
    waitForURL, response = Mock(), Mock()
    side_effect = [
        URLError('Fake Error'),
        (response, 'fake content')
    ]

    doWebRequest = Mock(side_effect=side_effect)

    # Patch doWebRequest and waitForURL so we do not make an http request.
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)
    monkeypatch.setattr('codalib.util.waitForURL', waitForURL)

    url = 'http://example.com/foo/bar'
    return_value = util.doWaitWebRequest(url)

    assert waitForURL.call_count == 1
    waitForURL.assert_called_with(url)
    assert return_value == (response, 'fake content')
