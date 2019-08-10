import pytest

from polytropos.actions.translate.__type_translator_registry import TypeTranslatorRegistry


class VarA:
    pass


class VarB(VarA):
    pass


class VarC1(VarB):
    pass


class VarC2(VarB):
    pass


class TranslatorA:
    pass


class TranslatorB:
    pass


class TranslatorC1:
    pass


@pytest.mark.parametrize("registration, expected", [
    ([], {VarA: ValueError, VarB: ValueError, VarC1: ValueError, VarC2: ValueError}),
    ([(VarB, TranslatorB)], {VarA: ValueError, VarB: TranslatorB, VarC1: TranslatorB, VarC2: TranslatorB}),
    ([(VarB, TranslatorB), (VarA, TranslatorA)], {VarA: TranslatorA, VarB: TranslatorB, VarC1: TranslatorB, VarC2: TranslatorB}),
    ([(VarB, TranslatorB), (VarA, TranslatorA), (VarC1, TranslatorC1)], {VarA: TranslatorA, VarB: TranslatorB, VarC1: TranslatorC1, VarC2: TranslatorB}),
])
def test_register_type_translators_for_hierarchy(monkeypatch, registration, expected):
    monkeypatch.setattr(TypeTranslatorRegistry, "registered", {})
    monkeypatch.setattr(TypeTranslatorRegistry, "cache", {})

    for variable_type, translator_type in registration:
        TypeTranslatorRegistry.register_translator_class(variable_type, translator_type)

    for variable_type, translator_type in expected.items():
        if isinstance(translator_type, type) and issubclass(translator_type, Exception):
            with pytest.raises(translator_type):
                _ = TypeTranslatorRegistry.get_translator_class(variable_type)
        else:
            assert TypeTranslatorRegistry.get_translator_class(variable_type) == translator_type
