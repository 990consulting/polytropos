def test_dt_no_restrictions(target_list_track):
    assert set(target_list_track.descendants_that()) == {
        "outside_list_primitive",
        "target_folder_outer",
        "target_folder_inner",
        "target_list",
        "target_list_name",
        "target_list_color",
        "target_named_list",
        "target_named_list_color"
    }

def test_dt_restrict_data_type(target_list_track):
    assert set(target_list_track.descendants_that(data_type="Text")) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color"
    }

def test_dt_primitive_inside_list(target_list_track):
    assert set(target_list_track.descendants_that(container=-1, inside_list=1)) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color"
    }

def test_dt_primitive_outside_list(target_list_track):
    assert set(target_list_track.descendants_that(container=-1, inside_list=-1)) == {
        "outside_list_primitive"
    }

def test_dt_primitive(target_list_track):
    assert set(target_list_track.descendants_that(container=-1)) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color",
        "outside_list_primitive"
    }

def test_dt_require_container(target_list_track):
    assert set(target_list_track.descendants_that(container=1)) == {
        "target_folder_outer",
        "target_folder_inner",
        "target_list",
        "target_named_list",
    }

def test_dt_require_specific_container(target_list_track):
    assert set(target_list_track.descendants_that(container=1, data_type="Folder")) == {
        "target_folder_outer",
        "target_folder_inner"
    }

def test_dt_require_specific_primitive(target_list_track):
    assert set(target_list_track.descendants_that(container=-1, data_type="Text")) == {
        "target_list_name",
        "target_list_color",
        "target_named_list_color"
    }

def test_dt_require_container_contradiction(target_list_track):
    assert set(target_list_track.descendants_that(container=1, data_type="Text")) == set()

def test_dt_require_primitive_contradiction(target_list_track):
    assert set(target_list_track.descendants_that(container=-1, data_type="Folder")) == set()

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
