class InstanceMatcher(object):
    """
    Mock argument matcher for objects passed to a mock instance.

    This will check that the argument is an instance of a class
    when passed to Mock.assert_called_with().
    """
    def __init__(self, cls):
        self.cls = cls

    def __eq__(self, obj):
        return isinstance(obj, self.cls)
