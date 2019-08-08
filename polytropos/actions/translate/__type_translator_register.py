from typing import Dict, Optional, Type

registered_type_translators: Dict[Optional[Type], Type] = {}

registered_type_translators_cache: Dict[Optional[Type], Type] = {}


def register_type_translator_class(variable_type: Type, translator_type: Type) -> None:
    registered_type_translators[variable_type] = translator_type
    registered_type_translators_cache.clear()


def get_type_translator_class(variable_type: Type) -> Type:
    type_translator_class: Optional[Type] = registered_type_translators_cache.get(variable_type, None)
    if type_translator_class is not None:
        return type_translator_class

    type_translator_class = registered_type_translators.get(variable_type, None)
    if type_translator_class is None:
        for base_variable_type in variable_type.__bases__:  # type: Type
            type_translator_class = get_type_translator_class(base_variable_type)
            if type_translator_class is not None:
                break

    if type_translator_class is None:
        raise ValueError

    registered_type_translators_cache[variable_type] = type_translator_class
    return type_translator_class

