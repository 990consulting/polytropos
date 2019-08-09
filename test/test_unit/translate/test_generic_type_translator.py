from unittest.mock import Mock

import pytest

from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.type_translators import GenericTypeTranslator


def test_translate_no_sources_listed(translator, document, variable):
    """If a variable is supposed to be translated but it has no sources, an exception should be raised."""
    variable.sources = []

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    with pytest.raises(SourceNotFoundException):
        _ = type_translator()


def test_translate_neither_source_has_values(translator, document, variable):
    """If a variable has sources but none have a value, an exception should be raised."""
    variable.sources = ["source1"]
    document.variable_value.side_effect = SourceNotFoundException

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    with pytest.raises(SourceNotFoundException):
        _ = type_translator()


def test_translate_first_source_has_value(translator, document, variable):
    """If a variable has two sources and the first one has a value, that value is captured."""
    variable.sources = ["source1"]
    document.variable_value.return_value = "source1_value"

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    translated = type_translator()
    assert translated == "source1_value"


def test_source_has_null_value(translator, document, variable):
    """If a variable's source has an explicit null value, the result is explicitly null."""
    variable.sources = ["source1"]
    document.variable_value.return_value = None

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    translated = type_translator()
    assert translated is None


def test_first_null_second_non_null(translator, document, variable):
    """If a variable has 2+ sources and the first extant one is explicitly null, the target is explicitly null."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return None
        return var.var_id + "_value"

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    translated = type_translator()
    assert translated is None


def test_translate_second_source_has_value(translator, document, variable):
    """If a variable has two sources and the second one has a value, that value is captured."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            raise SourceNotFoundException
        return var.var_id + "_value"

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    translated = type_translator()
    assert translated == "source2_value"


def test_translate_both_sources_have_values(translator, document, variable):
    """If a variable has multiple sources and more than one has a value, the first source with a value is used"""
    def variable_value(var, _parent_id):
        return var.var_id + "_value"

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value

    type_translator = GenericTypeTranslator(translator, document, variable, None)
    translated = type_translator()
    assert translated == "source1_value"


def test_translate_first_source_is_not_descendant(translator, document, variable):
    def variable_value(var, _parent_id):
        return var.var_id + "_value"

    parent_source = Mock()
    parent_source.check_ancestor = lambda source_id: source_id != "source1"

    parent_id = "parent"
    variable.sources = ["source1", "source2"]
    variable.track.source = {parent_id: parent_source}
    document.variable_value = variable_value

    type_translator = GenericTypeTranslator(translator, document, variable, parent_id)
    translated = type_translator()
    assert translated == "source2_value"
