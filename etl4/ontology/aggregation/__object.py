# TODO Quimey this is exactly the same situation as "subject" in metamorphosis/change, so handle this
#  however you handle that.
def object(*args, **kwargs):
    """Represents variables from the output schema."""
    def wrapper(f):
        return f
    return wrapper

