from typing import Type, Callable, Any


def lookup(name: str) -> Callable[[Type], Type]:
    """Intended to be a decorator on the constructor for a Change. Verifies that the specified lookup table has been
    loaded."""
    def decorator(cls: Type) -> Type:
        old_init = cls.__init__
        def __init__(self: Any, *args: Any, **kwargs: Any) -> None:
            old_init(self, *args, **kwargs)
            if name not in kwargs['lookups']:
                raise ValueError(f'Lookup {name} not loaded')
        cls.__init__ = __init__
        return cls
    return decorator
