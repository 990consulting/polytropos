from collections.abc import Callable

from etl4.ontology.metamorphosis.__change import Change

def lookup(func: Callable, name: str):
    """Intended to be a decorator on the constructor for a Change. Verifies that the specified lookup table has been
    loaded."""
    pass