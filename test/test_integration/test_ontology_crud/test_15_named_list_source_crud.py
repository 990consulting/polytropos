import pytest

def test_add_root_source():
    pytest.fail("IMPLEMENT ME: Adding a source to the root should not affect the children")

def test_delete_root_source():
    pytest.fail("IMPLEMENT ME: Removing a source from the root should delete the corresponding child sources")

def test_add_child_source():
    pytest.fail("IMPLEMENT ME: Adding a source to a child should be like adding any other source")

def test_add_child_source_not_descended_from_root_source_raises():
    pytest.fail("IMPLEMENT ME: Adding a source to a child that doesn't descend from a root source should fail.")

def test_add_out_of_scope_child_raises():
    pytest.fail("IMPLEMENT ME: In the nested list case, adding a source for a child of the INNER list that descends "
                "from a root of the OUTER list should fail.")

def test_remove_child_source():
    pytest.fail("IMPLEMENT ME: Removing a child source should be like removing any other source.")
