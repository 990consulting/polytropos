from collections.abc import Callable

from etl4.ontology.metamorphosis.__change import Change

# TODO Quimey I forget how parametrized decorators work, and maybe you'll think we shouldn't be using decorators at all
#  so just look at how I actually used this and decide how you want to implement it.
def lookup(*args, **kwargs):
    """Intended to be a decorator on the constructor for a Change. Verifies that the specified lookup table has been
    loaded."""
    pass