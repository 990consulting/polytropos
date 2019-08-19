from typing import Optional, Any
from unittest.mock import Mock

import pytest

from polytropos.actions.translate import Translator
from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.__type_translator_registry import TypeTranslatorRegistry


@pytest.fixture()
def source_track() -> Mock:
    return Mock()


@pytest.fixture()
def target_track(source_track) -> Mock:
    return Mock(source=source_track)


@pytest.fixture()
def type_translator_class() -> Mock:
    def translator(_translator, document, variable, _parent_id):
        translated = Mock()
        try:
            source_value = document.value([variable.name])
        except KeyError:
            raise SourceNotFoundException

        if isinstance(source_value, type) and issubclass(source_value, Exception):
            raise source_value

        return_value = source_value
        if isinstance(source_value, int):
            return_value = source_value + 100

        translated.return_value = return_value

        return translated

    translator_class = Mock()
    translator_class.return_value = translator
    return translator_class


def create_variable(var_id: str, name: str, parent_id: Optional[str]) -> Any:
    var = Mock(var_id=var_id)
    var.name = name
    var.parent = parent_id
    return var


def test_translate_no_target_variables(source_track, target_track):
    target_track.values.return_value = []
    document = {"a": 1}
    translator = Translator(target_track)

    translated = translator(document)
    assert translated == {}


def test_translate_one_target_variable(monkeypatch, source_track, target_track, type_translator_class):
    monkeypatch.setattr(TypeTranslatorRegistry, "get_translator_class", type_translator_class)

    target_track.values.return_value = [create_variable("id_a", "a", None)]
    document = {"a": 1, "b": 2}
    translator = Translator(target_track)

    translated = translator(document)
    assert translated == {"a": 101}


def test_translate_two_target_variables(monkeypatch, source_track, target_track, type_translator_class):
    monkeypatch.setattr(TypeTranslatorRegistry, "get_translator_class", type_translator_class)

    target_track.values.return_value = [create_variable("id_a", "a", None), create_variable("id_b", "b", None)]
    document = {"a": 1, "b": 2}
    translator = Translator(target_track)

    translated = translator(document)
    assert translated == {"a": 101, "b": 102}


def test_translate_missing_source(monkeypatch, source_track, target_track, type_translator_class):
    monkeypatch.setattr(TypeTranslatorRegistry, "get_translator_class", type_translator_class)

    target_track.values.return_value = [create_variable("id_a", "a", None), create_variable("id_b", "b", None), create_variable("id_c", "c", None)]
    document = {"a": 1, "b": 2}
    translator = Translator(target_track)

    translated = translator(document)
    assert translated == {"a": 101, "b": 102}


def test_translate_exception(monkeypatch, source_track, target_track, type_translator_class):
    monkeypatch.setattr(TypeTranslatorRegistry, "get_translator_class", type_translator_class)

    target_track.values.return_value = [create_variable("id_a", "a", None), create_variable("id_b", "b", None)]
    document = {"a": 1, "b": AttributeError}
    translator = Translator(target_track)

    with pytest.raises(AttributeError):
        _ = translator(document)
