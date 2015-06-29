from mock import Mock

from codalib import util

from . import InstanceMatcher


def test_return_value(monkeypatch):
    """
    Check the return value of doWebRequest.
    """
    # Setup the mocks.
    response = Mock()
    response.read.return_value = 'test content'
    mock_urlopen = Mock(return_value=response)

    # Patch urlopen so that we do not make an http request.
    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)

    return_value = util.doWebRequest('http://exmple.com/foo/bar')
    assert return_value == (response, response.read())


def test_return_response_is_none(monkeypatch):
    """
    Verify the return value is (None, None) when the HTTP Response
    is falsy.
    """
    mock_urlopen = Mock(return_value=None)
    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)

    return_value = util.doWebRequest('http://exmple.com/foo/bar')
    assert return_value == (None, None)


def test_with_head_method(monkeypatch):
    """
    Check that the HEADREQUEST is passed to urllib2.urlopen.
    """
    response = Mock()
    response.read.return_value = 'test content'
    mock_urlopen = Mock(return_value=response)

    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)
    return_value = util.doWebRequest('http://example.com/foo/bar',
                                     method='HEAD')

    assert return_value == (response, response.read())

    matcher = InstanceMatcher(util.HEADREQUEST)
    mock_urlopen.assert_called_with(matcher)


def test_with_put_method(monkeypatch):
    """
    Check that the PUTREQUEST is passed to urllib2.urlopen.
    """
    response = Mock()
    response.read.return_value = 'test content'
    mock_urlopen = Mock(return_value=response)

    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)
    return_value = util.doWebRequest('http://example.com/foo/bar',
                                     method='PUT')

    assert return_value == (response, response.read())

    matcher = InstanceMatcher(util.PUTREQUEST)
    mock_urlopen.assert_called_with(matcher)


def test_with_delete_method(monkeypatch):
    """
    Check that the DELETEREQUEST is passed to urllib2.urlopen.
    """
    response = Mock()
    response.read.return_value = 'test content'
    mock_urlopen = Mock(return_value=response)

    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)
    return_value = util.doWebRequest('http://example.com/foo/bar',
                                     method='DELETE')

    assert return_value == (response, response.read())

    matcher = InstanceMatcher(util.DELETEREQUEST)
    mock_urlopen.assert_called_with(matcher)


def test_with_post_method(monkeypatch):
    """
    Check that a urllib2.Request object with the POST method is
    constructed.
    """
    request, response = Mock(), Mock()
    response.read.return_value = 'test content'
    mock_urlopen = Mock(return_value=response)

    # We will mock the request object so we can make some
    # assertions about how it was called.
    monkeypatch.setattr('urllib2.Request', request)
    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)

    url = 'http://example.com/foo/bar'
    data = {'data': 'test'}
    return_value = util.doWebRequest(url, data=data, method='POST')

    assert return_value == (response, response.read())
    request.assert_called_with(url, data=data, headers={})


def test_with_get_method(monkeypatch):
    """
    Check that a urllib2.Request object with the GET method is
    constructed.
    """
    request, response = Mock(), Mock()
    response.read.return_value = 'test content'
    mock_urlopen = Mock(return_value=response)

    monkeypatch.setattr('urllib2.Request', request)
    monkeypatch.setattr('urllib2.urlopen', mock_urlopen)

    url = 'http://example.com/foo/bar'
    return_value = util.doWebRequest(url)

    assert return_value == (response, response.read())
    request.assert_called_with(url, headers={})
