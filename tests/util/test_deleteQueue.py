from mock import Mock
import pytest

from codalib import util


def test_is_successful(monkeypatch):
    """
    Check that deleteQueue does not raise an exception and that
    doWebRequest and response.getcode are called once.
    """
    response = Mock()
    response.getcode.return_value = 200

    expected = (response, 'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    util.deleteQueue('/foo/bar', 'ark:/0001')

    assert response.getcode.call_count == 1
    assert doWebRequest.call_count == 1


def test_raises_exception(monkeypatch):
    """
    Check that an exception is raised if the response is returned
    without a status code 200.
    """
    response = Mock()
    response.getcode.return_value = 201

    expected = (response, 'Fake content')
    doWebRequest = Mock(return_value=expected)
    monkeypatch.setattr('codalib.util.doWebRequest', doWebRequest)

    with pytest.raises(Exception):
        util.deleteQueue('/foo/bar', 'ark:/0001')
