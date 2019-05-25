from collections.abc import Callable
from typing import Optional, Set

# TODO Quimey I forget how parametrized decorators work, and maybe you'll think we shouldn't be using decorators at all
#  so just look at how I actually used this and decide how you want to implement it.
def subject(*args, **kwargs):
    """Used as a decorator on the constructor for a Change. At construction time, the decorator validates that a
    particular variable ID meets the conditions specified, and then replaces it with a Variable object.

    :param data_types: a set of acceptable data types for the subject.
    :param temporal: If 1, require a temporal variable; if -1; require an invariant variable. (If 0, no restriction.)"""
    def wrapper(f):
        return f
    return wrapper
