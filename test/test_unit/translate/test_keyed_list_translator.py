from unittest.mock import Mock

import pytest

from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.type_translators import KeyedListTranslator


def test_no_sources(translator, document, variable):
    """No sources defined - raises an exception."""
    variable.sources = []
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    with pytest.raises(SourceNotFoundException):
        _ = type_translator()


def test_two_sources_both_missing(translator, document, variable):
    """Two sources defined, but both are missing from the source document - raises an exception."""
    variable.sources = ["source1", "source2"]
    document.variable_value.side_effect = SourceNotFoundException
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    with pytest.raises(SourceNotFoundException):
        _ = type_translator()


def test_two_sources_both_empty(translator, document, variable):
    """Two sources defined, and both are present but empty; empty dict is returned."""
    variable.sources = ["source1", "source2"]
    document.variable_value.return_value = {}
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    assert type_translator() == {}


def test_one_source(translator, document, variable):
    """One source is specified; a target list is made from that source."""
    variable.sources = ["source1"]
    document.variable_value.return_value = {"a": 1, "b": 2}
    translator.translate = lambda doc, _parent_id, _source_parent_id: 100 + doc
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    assert type_translator() == {"a": 101, "b": 102}


def test_two_sources_one_empty(translator, document, variable):
    """Two sources are defined, but one is empty."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return {}
        return {"a": 1, "b": 2}

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value
    translator.translate = lambda doc, _parent_id, _source_parent_id: 100 + doc
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    translated = type_translator()
    assert translated == {"a": 101, "b": 102}


def test_combine_lists(translator, document, variable):
    """When two sources both have items, they get combined into one dict."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return {"a": 1, "b": 2}
        return {"c": 3, "d": 4, "e": 5}

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value
    translator.translate = lambda doc, _parent_id, _source_parent_id: 100 + doc
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    translated = type_translator()
    assert translated == {"a": 101, "b": 102, "c": 103, "d": 104, "e": 105}


def test_duplicate_name_raises(translator, document, variable):
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return {"a": 1, "b": 2}
        return {"a": 3}

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value
    translator.translate = lambda doc, _parent_id, _source_parent_id: 100 + doc
    parent_id = None

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    with pytest.raises(ValueError):
        _ = type_translator()


def test_translate_first_source_is_not_descendant(translator, document, variable):
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return {"a": 1, "b": 2}
        return {"c": 3, "d": 4, "e": 5}

    parent_source = Mock()
    parent_source.check_ancestor = lambda source_id: source_id != "source1"

    parent_id = "parent"
    variable.sources = ["source1", "source2"]
    variable.track.source = {parent_id: parent_source}
    document.variable_value = variable_value
    translator.translate = lambda doc, _parent_id, _source_parent_id: 100 + doc

    type_translator = KeyedListTranslator(translator, document, variable, parent_id)
    translated = type_translator()
    assert translated == {"c": 103, "d": 104, "e": 105}

