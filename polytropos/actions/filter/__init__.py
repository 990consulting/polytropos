from polytropos.actions.filter._filter import Filter

def register_filter_subclasses() -> None:
    """Import all built-in subclasses so that they can be used in tasks"""
    from polytropos.actions.filter.firstlast import EarliestFilter, LatestFilter
    from polytropos.actions.filter.values.has_all import HasAllSpecificValues
    from polytropos.actions.filter.values.has_any import HasAnySpecificValues
    from polytropos.actions.filter.comparison import AtLeast, AtMost, GreaterThan, LessThan, NotEqualTo
    from polytropos.actions.filter.exists import Exists