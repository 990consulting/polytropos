from typing import Dict

import pytest

@pytest.fixture()
def list_with_outside_primitives(target_list_track):
    outside_list_primitive_spec: Dict = {
        "name": "some primitive",
        "data_type": "Integer",
        "sort_order": 0
    }
    target_list_track.add(outside_list_primitive_spec, "outside_list_primitive")
    return target_list_track

def test_dt_no_restrictions(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that()) == {
        "outside_list_primitive",
        "target_folder_outer",
        "target_folder_inner",
        "target_list",
        "target_list_name",
        "target_list_color",
        "target_named_list",
        "target_named_list_color"
    }

def test_dt_restrict_data_type(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(data_type="Text")) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color"
    }

def test_dt_primitive_inside_list(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=-1, inside_list=1)) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color"
    }

def test_dt_primitive_outside_list(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=-1, inside_list=-1)) == {
        "outside_list_primitive"
    }

def test_dt_primitive(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=-1)) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color",
        "outside_list_primitive"
    }

def test_dt_require_container(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=1)) == {
        "target_folder_outer",
        "target_folder_inner",
        "target_list",
        "target_named_list",
    }

def test_dt_require_specific_container(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=1, data_type="Folder")) == {
        "target_folder_outer",
        "target_folder_inner"
    }

def test_dt_require_specific_primitive(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=-1, data_type="Text")) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color"
    }

def test_dt_require_container_contradiction(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=1, data_type="Text")) == set()

def test_dt_require_primitive_contradiction(list_with_outside_primitives):
    assert set(list_with_outside_primitives.descendants_that(container=-1, data_type="Folder")) == set()

def test_dt_require_targets(target_list_track):
    # TODO The fixture needs to be updated to reflect the new list source handling setup
    source_list_track = target_list_track.source
    assert set(source_list_track.descendants_that(targets=1)) == {
        "source_list",
        "source_list_name",
        "source_list_color",
        "source_named_list",
        "source_named_list_color"
    }

def test_dt_require_no_targets(target_list_track):
    # TODO The fixture needs to be updated to reflect the new list source handling setup
    source_list_track = target_list_track.source
    assert set(source_list_track.descendants_that(targets=-1)) == {
        "source_folder",
        "random_text_field"
    }

def test_dt_require_primitive_with_targets(target_list_track):
    # TODO The fixture needs to be updated to reflect the new list source handling setup
    source_list_track = target_list_track.source
    assert set(source_list_track.descendants_that(targets=1, container=-1)) == {
        "source_list_name",
        "source_list_color",
        "source_named_list_color"
    }

def test_dt_require_container_with_targets(target_list_track):
    source_list_track = target_list_track.source
    assert set(source_list_track.descendants_that(targets=1, container=1)) == {
        "source_list",
        "source_named_list"
    }
