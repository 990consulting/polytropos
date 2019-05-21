from collections.abc import Callable
from typing import Optional, Set

def subject(func: Callable, name: str, data_types: Optional[Set]=None, temporal: Optional[int]=0):
    """Used as a decorator on the constructor for a Change. At construction time, the decorator validates that a
    particular variable ID meets the conditions specified, and then replaces it with a Variable object.

    :param data_types: a set of acceptable data types for the subject.
    :param temporal: If 1, require a temporal variable; if -1; require an invariant variable. (If 0, no restriction.)"""
    pass
