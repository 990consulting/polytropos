from typing import Dict, Type, Any
import logging

def _crawl_subclasses(cls: Type, ret: Dict) -> None:
    for subclass in cls.__subclasses__():
        name: str = subclass.__name__
        ret[name] = subclass
        _crawl_subclasses(subclass, ret)

def load(klass: Type) -> Dict[str, Type]:
    """Returns a map of subclass name to actual subclass."""
    logging.info('Loading all known subclasses of "%s".' % klass.__name__)
    ret: Dict[str, Any] = {}
    _crawl_subclasses(klass, ret)
    return ret
