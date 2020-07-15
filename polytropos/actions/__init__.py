from polytropos.actions.aggregate import register_aggregate_subclasses
from polytropos.actions.consume import register_consume_subclasses
from polytropos.actions.changes import register_change_subclasses
from polytropos.actions.filter import register_filter_subclasses
from polytropos.actions.scan import register_scan_subclasses
from polytropos.actions.translate import register_translate_subclasses
from polytropos.actions.merge import Merge

def register_all() -> None:
    register_aggregate_subclasses()
    register_consume_subclasses()
    register_change_subclasses()
    register_filter_subclasses()
    register_scan_subclasses()
    register_translate_subclasses()
