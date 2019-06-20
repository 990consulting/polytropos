from typing import Dict, Type
import logging

def load(klass: Type) -> Dict[str, Type]:
    """Returns a map of subclass name to actual subclass."""
    logging.info('Loading all known subclasses of "%s".' % klass.__name__)
    ret: Dict[str, Type] = {}
    for cls in klass.__subclasses__():
        logging.debug('   Found subclass "%s" of "%s".' % (cls.__name__, klass.__name__))
        ret[cls.__name__] = cls
    return {
        cls.__name__: cls
        for cls in klass.__subclasses__()
    }
