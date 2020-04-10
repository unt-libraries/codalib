from datetime import datetime
from unittest.mock import Mock, patch, mock_open, call
from urllib.error import URLError

import pytest

from codalib import util


EVENT = b"""<?xml version="1.0"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title>20b28e4ee56811e9905154bf64888bf3</title>
  <id>20b28e4ee56811e9905154bf64888bf3</id>
  <updated>2019-10-02T17:58:19.982448-05:00</updated>
  <content type="application/xml">
    <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
      <premis:eventIdentifier>
        <premis:eventIdentifierType>http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID</premis:eventIdentifierType>
        <premis:eventIdentifierValue>20b28e4ee56811e9905154bf64888bf3</premis:eventIdentifierValue>
      </premis:eventIdentifier>
      <premis:eventType/>
      <premis:eventDateTime>2019-10-02T22:58:19</premis:eventDateTime>
      <premis:eventDetail/>
      <premis:eventOutcomeInformation>
        <premis:eventOutcome/>
      </premis:eventOutcomeInformation>
      <premis:linkingAgentIdentifier>
        <premis:linkingAgentIdentifierType>http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL</premis:linkingAgentIdentifierType>
        <premis:linkingAgentIdentifierValue/>
        <premis:linkingAgentRole>http://purl.org/net/untl/vocabularies/linkingAgentRoles/#executingProgram</premis:linkingAgentRole>
      </premis:linkingAgentIdentifier>
    </premis:event>
  </content>
</entry>
"""


@patch('codalib.util.doWebRequest')
@patch('codalib.util.uuid.uuid4')
@patch('codalib.util.uuid.uuid1')
@patch('codalib.bagatom.xsDateTime_format', return_value='2019-10-02T17:58:19.982448-05:00')
def test_is_successful(mock_xsdt, mock_uuid1, mock_uuid4, mock_doWebRequest):
    """
    Check that sendPremisEvent returns the response and content.

    Verify the conditions will cause no exceptions to be
    raised or caught.
    """
    response = Mock(code=201)
    expected = (response, 'Fake content')
    mock_doWebRequest.return_value = expected
    mock_uuid1.return_value.hex = mock_uuid4.return_value.hex = '20b28e4ee56811e9905154bf64888bf3'

    actual = util.sendPREMISEvent('http://example.com', None, None, None, None,
                                  eventDate=datetime(2019, 10, 2, 22, 58, 19))

    assert actual == expected
    mock_doWebRequest.assert_called_once_with('http://example.com', 'POST', data=EVENT)


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

    expected = (response, b'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    with pytest.raises(Exception):
        util.sendPREMISEvent('http://example.com', None, None, None, None)

    assert doWebRequest.call_count == 1


def test_raises_exception_without_201_status_with_debug(monkeypatch):
    """
    Verify that response content is written to file when sendPREMISEvent
    will raise an exception when the returned response does not have a
    status code 201 with debug=True.
    """
    response = Mock(code=200)

    expected = (response, b'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    m = mock_open()

    with pytest.raises(Exception):
        with patch('codalib.util.open', m):
            util.sendPREMISEvent('http://example.com', None, None, None, None, debug=True)

    calls = [call().write(b'Fake content'), call().close()]
    m.assert_has_calls(calls)
    assert doWebRequest.call_count == 1
