def lookup(name):
    """Intended to be a decorator on the constructor for a Change. Verifies that the specified lookup table has been
    loaded."""
    def decorator(cls):
        old_init = cls.__init__
        def __init__(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            if name not in kwargs['lookups']:
                raise ValueError(f'Lookup {name} not loaded')
        cls.__init__ = __init__
        return cls
    return decorator
