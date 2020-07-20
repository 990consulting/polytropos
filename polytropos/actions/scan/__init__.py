from polytropos.actions.scan._scan import Scan

def register_scan_subclasses() -> None:
    """Import all built-in subclasses so that they can be used in tasks"""
    import polytropos.actions.scan.quantile
    import polytropos.actions.scan.rank
