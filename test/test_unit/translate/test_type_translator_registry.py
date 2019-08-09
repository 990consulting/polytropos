import pytest

from polytropos.actions.translate.__type_translator_registry import TypeTranslatorRegistry


def test_register_type_translators_for_hierarchy(monkeypatch):
    monkeypatch.setattr(TypeTranslatorRegistry, "registered", {})
    monkeypatch.setattr(TypeTranslatorRegistry, "cache", {})

    class A:
        pass

    class B(A):
        pass

    class C1(B):
        pass

    class C2(B):
        pass

    class TranslatorA:
        pass

    class TranslatorB:
        pass

    class TranslatorC1:
        pass

    with pytest.raises(ValueError):
        _ = TypeTranslatorRegistry.get_translator_class(A)
    with pytest.raises(ValueError):
        _ = TypeTranslatorRegistry.get_translator_class(B)
    with pytest.raises(ValueError):
        _ = TypeTranslatorRegistry.get_translator_class(C1)
    with pytest.raises(ValueError):
        _ = TypeTranslatorRegistry.get_translator_class(C2)

    TypeTranslatorRegistry.register_translator_class(B, TranslatorB)

    with pytest.raises(ValueError):
        _ = TypeTranslatorRegistry.get_translator_class(A)
    assert TypeTranslatorRegistry.get_translator_class(B) == TranslatorB
    assert TypeTranslatorRegistry.get_translator_class(C1) == TranslatorB
    assert TypeTranslatorRegistry.get_translator_class(C2) == TranslatorB

    TypeTranslatorRegistry.register_translator_class(A, TranslatorA)

    assert TypeTranslatorRegistry.get_translator_class(A) == TranslatorA
    assert TypeTranslatorRegistry.get_translator_class(B) == TranslatorB
    assert TypeTranslatorRegistry.get_translator_class(C1) == TranslatorB
    assert TypeTranslatorRegistry.get_translator_class(C2) == TranslatorB

    TypeTranslatorRegistry.register_translator_class(C1, TranslatorC1)

    assert TypeTranslatorRegistry.get_translator_class(A) == TranslatorA
    assert TypeTranslatorRegistry.get_translator_class(B) == TranslatorB
    assert TypeTranslatorRegistry.get_translator_class(C1) == TranslatorC1
    assert TypeTranslatorRegistry.get_translator_class(C2) == TranslatorB
