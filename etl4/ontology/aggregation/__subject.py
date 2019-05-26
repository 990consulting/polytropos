# TODO Quimey this is exactly the same situation as "subject" in metamorphosis/change, so handle this
#  however you handle that.
def subject(*args, **kwargs):
    """Represents variables from the input schema."""
    def wrapper(f):
        return f
    return wrapper
