def register_change_subclasses() -> None:
    """Import all built-in Change subclasses so that they can be accessed by tasks."""
    import polytropos.actions.changes.cast
    import polytropos.actions.changes.prune
    import polytropos.actions.changes.available
    import polytropos.actions.changes.stat
    import polytropos.actions.changes.delete
    import polytropos.actions.changes.sort
    import polytropos.actions.changes.display