from polytropos.actions.consume._consume import Consume

def register_consume_subclasses():
    """Import all built-in subclasses so that they can be used in tasks"""
    from polytropos.actions.consume.tojson import ExportToJSON