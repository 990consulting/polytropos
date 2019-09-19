def register_change_subclasses() -> None:
    """Import all built-in Change subclasses so that they can be accessed by tasks."""
    from polytropos.actions.changes.cast import Cast
    from polytropos.actions.changes.prune import Prune