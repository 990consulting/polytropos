import copy
from typing import Dict, List, Set

import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

@pytest.fixture
def nested_new_var_spec() -> Dict:
    return {
        "name": "the new one",  # Note -- spaces are OK!
        "data_type": "Integer",
        "parent": "target_folder_2",
        "sort_order": 1
    }

def test_add_adds_to_track_variable_table(target_nested_dict_track, nested_new_var_spec):
    track: Track = target_nested_dict_track
    track.add(nested_new_var_spec, "A")
    new_var: Variable = track["A"]
    new_var_dict: Dict = new_var.dump()
    assert new_var_dict == nested_new_var_spec

def test_add_changes_track_list(target_nested_dict_track, nested_new_var_spec):
    track: Track = target_nested_dict_track

    track_spec_old: Dict = track.dump()
    expected: Dict = copy.deepcopy(track_spec_old)
    expected["A"] = nested_new_var_spec

    track.add(nested_new_var_spec, "A")

    actual: Dict = track.dump()
    assert actual == expected

def test_add_variable_without_id_generates_default(target_nested_dict_track, nested_new_var_spec):
    """If no ID is supplied, use <stage name>_<temporal|invarant>_<n+1>, where n is the number of variables."""

    track: Track = target_nested_dict_track

    track_spec_old: Dict = track.dump()
    expected: Dict = copy.deepcopy(track_spec_old)
    expected["Target_5"] = nested_new_var_spec

    track.add(nested_new_var_spec)

    actual: Dict = track.dump()
    assert actual == expected

def test_add_track_non_unique_id_raises(target_nested_dict_track, nested_new_var_spec):
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "target_var_2")

def test_add_locally_non_unique_name_raises(target_nested_dict_track, nested_new_var_spec):
    nested_new_var_spec["name"] = "second_target"
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "A")

@pytest.mark.parametrize("illegal_name", ["/I have a slash", "I.Have.Periods"])
def test_add_illegal_name_raises(illegal_name, target_nested_dict_track, nested_new_var_spec):
    nested_new_var_spec["name"] = illegal_name
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "A")

def test_add_empty_var_id_raises(target_nested_dict_track, nested_new_var_spec):
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "")

def test_add_invalid_source_raises(target_nested_dict_track, nested_new_var_spec):
    nested_new_var_spec["sources"] = ["non-existent source"]
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "A")

def test_add_with_sources_alters_source_of_for_source(target_nested_dict_track, nested_new_var_spec):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    nested_new_var_spec["sources"] = ["source_var_1"]
    target_nested_dict_track.add(nested_new_var_spec, "A")

    source_var: Variable = source_track["source_var_1"]
    actual: Set = set(source_var.targets())
    expected: Set = {"A", "target_var_1"}
    assert actual == expected

def test_add_with_sources_alters_has_targets_for_source_after(target_nested_dict_track, nested_new_var_spec):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    nested_new_var_spec["sources"] = ["source_var_3"]
    target_nested_dict_track.add(nested_new_var_spec, "A")

    source_var: Variable = source_track["source_var_3"]
    assert source_var.has_targets

def test_add_with_parent_alters_children_for_parent_after(target_nested_dict_track, nested_new_var_spec):
    target_nested_dict_track.add(nested_new_var_spec, "A")
    target_folder_2: Variable = target_nested_dict_track["target_folder_2"]

    expected: Set = {"target_var_2", "A"}
    actual: Set = set(
        map(lambda child: child.var_id, target_folder_2.children)
    )
    assert expected == actual

def test_add_non_container_parent_raises(target_nested_dict_track, nested_new_var_spec):
    nested_new_var_spec["parent"] = "target_var_1"
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "A")

def test_add_non_existent_parent_raises(target_nested_dict_track, nested_new_var_spec):
    nested_new_var_spec["parent"] = "non-existent parent"
    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "A")

def test_add_no_sort_order_change(target_nested_dict_track, nested_new_var_spec):
    target_nested_dict_track.add(nested_new_var_spec, "A")

    target_var_2: Variable = target_nested_dict_track["target_var_2"]
    assert target_var_2.sort_order == 0

def test_add_pushes_sort_order_down(target_nested_dict_track, nested_new_var_spec):
    """If the new variable has a sort order lower than the highest sort order, it pushes down all others at that
    level."""
    nested_new_var_spec["sort_order"] = 0
    target_nested_dict_track.add(nested_new_var_spec, "A")

    target_var_2: Variable = target_nested_dict_track["target_var_2"]
    assert target_var_2.sort_order == 1

def test_invalid_sort_order_raises(target_nested_dict_track, nested_new_var_spec):
    nested_new_var_spec["sort_order"] = 5

    with pytest.raises(ValueError):
        target_nested_dict_track.add(nested_new_var_spec, "A")

def test_add_alters_descendants_that(target_nested_dict_track, nested_new_var_spec):
    track: Track = target_nested_dict_track
    track.add(nested_new_var_spec, "A")
    actual: Set[str] = {"A", "target_var_1", "target_var_2"}
    expected: Set[str] = set(track.descendants_that(container=-1))
    assert actual == expected

