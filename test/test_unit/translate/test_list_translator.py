from unittest.mock import Mock

import pytest

from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.type_translators import ListTranslator


def test_no_sources(translator, document, variable):
    """No sources defined - raises an exception."""
    variable.sources = []

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    with pytest.raises(SourceNotFoundException):
        _ = type_translator()


def test_two_sources_both_missing(translator, document, variable):
    """Two sources defined, but both are missing from the source document; an empty list is created."""
    variable.sources = ["source1", "source2"]
    document.variable_value.side_effect = SourceNotFoundException

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    assert type_translator() == []


def test_two_sources_both_empty(translator, document, variable):
    """Two sources defined, and both are present but empty; an empty list is created."""
    variable.sources = ["source1", "source2"]
    document.variable_value.return_value = []

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    assert type_translator() == []


def test_one_source(translator, document, variable):
    """One source is specified; a result list is made from that source."""
    variable.sources = ["source1"]
    document.variable_value.return_value = [1, 2, 3]
    translator.translate = lambda _composite_id, _period, doc, _parent_id, _source_parent_id: 100 + doc

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    assert type_translator() == [101, 102, 103]


def test_two_sources_one_empty(translator, document, variable):
    """Two sources are defined, but one is empty."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return []
        return [1, 2, 3]

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value
    translator.translate = lambda _composite_id, _period, doc, _parent_id, _source_parent_id: 100 + doc

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    translated = type_translator()
    assert translated == [101, 102, 103]


def test_combine_lists(translator, document, variable):
    """When two sources both have items, they get combined into one list."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return [1, 2, 3]
        return [4, 5]

    variable.sources = ["source1", "source2"]
    document.variable_value = variable_value
    translator.translate = lambda _composite_id, _period, doc, _parent_id, _source_parent_id: 100 + doc

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    translated = type_translator()
    assert translated == [101, 102, 103, 104, 105]


def test_source_order_matters(translator, document, variable):
    """Reversing the order of the sources in an equivalent change in the order of the
    resulting list."""
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return [1, 2, 3]
        return [4, 5]

    variable.sources = ["source2", "source1"]
    document.variable_value = variable_value
    translator.translate = lambda _composite_id, _period, doc, _parent_id, _source_parent_id: 100 + doc

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    translated = type_translator()
    assert translated == [104, 105, 101, 102, 103]


def test_source_is_dict(translator, document, variable):
    variable.sources = ["source1"]
    document.variable_value.return_value = {"a": 1}
    translator.translate = lambda _composite_id, _period, doc, _parent_id, _source_parent_id: {"aa": doc["a"] + 100}

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, None)
    assert type_translator() == [{"aa": 101}]


def test_translate_first_source_is_not_descendant(translator, document, variable):
    def variable_value(var, _parent_id):
        if var.var_id == "source1":
            return [1, 2, 3]
        return [4, 5]

    parent_source = Mock()
    parent_source.check_ancestor = lambda source_id: source_id != "source1"

    parent_id = "parent"
    variable.sources = ["source1", "source2"]
    variable.track.source = {parent_id: parent_source}
    document.variable_value = variable_value
    translator.translate = lambda _composite_id, _period, doc, _parent_id, _source_parent_id: 100 + doc

    type_translator = ListTranslator(translator, "composite_id", "period", document, variable, parent_id)
    translated = type_translator()
    assert translated == [104, 105]

