from urllib2 import Request

from codalib import util


class TestHEADREQUEST(object):

    def test_subclass_of_Request(self):
        """
        Test that HEADREQUEST is a subclass of urllib2.Request.
        """
        assert issubclass(util.HEADREQUEST, Request)

    def test_get_method(self):
        """
        Verify the HTTP method is HEAD.
        """
        request = util.HEADREQUEST('http://example.com')
        assert request.get_method() == 'HEAD'


class TestPUTREQUEST(object):

    def test_subclass_of_Request(self):
        """
        Test that PUTREQUEST is a subclass of urllib2.Request.
        """
        assert issubclass(util.PUTREQUEST, Request)

    def test_get_method(self):
        """
        Verify the HTTP method is PUT.
        """
        request = util.PUTREQUEST('http://example.com')
        assert request.get_method() == 'PUT'


class TestDELETEREQUEST(object):

    def test_subclass_of_Request(self):
        """
        Test that DELETEREQUEST is a subclass of urllib2.Request.
        """
        assert issubclass(util.DELETEREQUEST, Request)

    def test_get_method(self):
        """
        Verify the HTTP method is DELETE.
        """
        request = util.DELETEREQUEST('http://example.com')
        assert request.get_method() == 'DELETE'
