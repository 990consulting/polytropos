from typing import Dict, List
import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

def test_alter_source_changes_sources_list(target_nested_dict_track):
    track: Track = target_nested_dict_track
    var: Variable = track["target_var_2"]
    var.sources = ["source_var_2", "source_var_3"]
    assert var.sources == ["source_var_2", "source_var_3"]

def do_source_swap(track: Track) -> Variable:
    var: Variable = track["target_var_2"]
    var.sources = ["source_var_3"]
    return var

def test_alter_source_changes_dict(target_nested_dict_track):
    var: Variable = do_source_swap(target_nested_dict_track)
    expected: Dict = {
        "name": "second_target",
        "data_type": "Integer",
        "sources": ["source_var_3"],
        "parent": "target_folder_2",
        "sort_order": 0
    }
    actual: Dict = var.dump()
    assert expected == actual

def test_add_source_alters_source_for_vars_in(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    assert set(source_track["source_var_3"].targets()) == set()
    do_source_swap(target_track)
    assert set(source_track["source_var_3"].targets()) == {"target_var_2"}

def test_remove_source_alters_targets(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    assert set(source_track["source_var_2"].targets()) == {"target_var_2"}
    do_source_swap(target_track)
    assert set(source_track["source_var_2"].targets()) == set()

def test_add_source_changes_has_targets(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    assert not source_track["source_var_3"].has_targets
    do_source_swap(target_track)
    assert source_track["source_var_3"].has_targets

def test_remove_source_changes_has_targets(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    assert source_track["source_var_2"].has_targets
    do_source_swap(target_track)
    assert not source_track["source_var_2"].has_targets

def test_nonexistent_source_raises(target_nested_dict_track):
    with pytest.raises(ValueError):
        target_nested_dict_track["target_var_2"].sources = ["Not a thing"]

def test_incompatible_source_raises(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    text_var_spec: Dict = {
        "name": "a text variable",
        "data_type": "Text",
        "sort_order": 2
    }
    source_track.add(text_var_spec, "source_text_var")

    with pytest.raises(ValueError):
        target_track["target_var_2"].sources = ["source_text_var"]

@pytest.mark.parametrize("sources", [
    [],
    ["source_var_2"],
    ["source_var_2", "source_var_3"]
])
def test_add_source_to_folder_raises(sources, target_nested_dict_track):
    track: Track = target_nested_dict_track
    folder: Variable = track["target_folder_1"]
    with pytest.raises(ValueError):
        folder.sources = sources
