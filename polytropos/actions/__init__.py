from polytropos.actions.aggregate import register_aggregate_subclasses
from polytropos.actions.consume import register_consume_subclasses
from polytropos.actions.changes import register_change_subclasses
from polytropos.actions.filter import register_filter_subclasses
from polytropos.actions.scan import register_scan_subclasses

def register_all():
    register_aggregate_subclasses()
    register_consume_subclasses()
    register_change_subclasses()
    register_filter_subclasses()
    register_scan_subclasses()
