import pytest

def test_change_parent_alters_relative_path():
    """moving a variable to a new parent changes its path."""
    pytest.fail()

def test_change_parent_alters_absolute_path():
    pytest.fail()

def test_change_parent_alters_original_parent_children():
    pytest.fail()

def test_change_parent_alters_new_parent_children():
    pytest.fail()

def test_change_parent_alters_original_descendants_that():
    """after changing the parent, the original parent no longer includes the node in descendents_that()."""
    pytest.fail()

def test_change_parent_alters_new_descendants_that():
    """after changing the parent, the new parent includes the node in descendents_that()."""
    pytest.fail()

def test_change_parent_cascades_on_descendants_that():
    """changing the parent of a variable affects descendants_that() for upstream antecedents."""
    pytest.fail()

def test_change_parent_of_list_descendent_raises():
    """attempting to change the topology of list descendents is illegal."""
    pytest.fail()

def test_change_parent_does_not_affect_source_status():
    """moving a variable does not alter its status as a source."""
    pytest.fail()

def test_change_parent_does_not_affect_target_status():
    """moving a variable does not alter its status as a target."""
    pytest.fail()

def test_change_parent_alters_json():
    """changing a variable's parent alters its json representation."""
    pytest.fail()

def test_change_parent_alters_tree():
    """changing a variable's parent alters the tree from the parent onward."""
    pytest.fail()

def test_move_to_non_container_raises():
    pytest.fail()

def test_move_to_nonexistent_parent_raises():
    pytest.fail()