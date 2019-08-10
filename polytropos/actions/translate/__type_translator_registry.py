from typing import Dict, Optional, Type


class TypeTranslatorRegistry:
    registered: Dict[Optional[Type], Type] = {}

    cache: Dict[Optional[Type], Type] = {}

    @staticmethod
    def register_translator_class(variable_type: Type, translator_type: Type) -> None:
        TypeTranslatorRegistry.registered[variable_type] = translator_type
        TypeTranslatorRegistry.cache.clear()

    @staticmethod
    def get_translator_class(variable_type: Type) -> Type:
        type_translator_class: Optional[Type] = TypeTranslatorRegistry.cache.get(variable_type, None)
        if type_translator_class is not None:
            return type_translator_class

        type_translator_class = TypeTranslatorRegistry.registered.get(variable_type, None)
        if type_translator_class is None:
            for base_variable_type in variable_type.__bases__:  # type: Type
                type_translator_class = TypeTranslatorRegistry.get_translator_class(base_variable_type)
                if type_translator_class is not None:
                    break

        if type_translator_class is None:
            raise ValueError

        TypeTranslatorRegistry.cache[variable_type] = type_translator_class
        return type_translator_class

