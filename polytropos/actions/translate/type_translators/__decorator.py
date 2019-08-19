from typing import Type, Callable

from polytropos.actions.translate.__type_translator_registry import TypeTranslatorRegistry


def type_translator(variable_type: Type) -> Callable[[Type], Type]:
    def wrap(cls: Type) -> Type:
        TypeTranslatorRegistry.register_translator_class(variable_type, cls)
        return cls

    return wrap
