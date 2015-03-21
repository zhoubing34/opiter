
class CallableEntry:
    """Can be used in a DynamicDict to wrap a function."""
    def __init__(self, function):
        self.function = function
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
