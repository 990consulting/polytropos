from polytropos.actions.translate.__translator import Translator
from polytropos.actions.translate.__translate import Translate
import polytropos.actions.translate.type_translators


def register_translate_subclasses() -> None:
    """Import all built-in subclasses so that they can be used in tasks"""
    from polytropos.actions.translate.trace import Trace
