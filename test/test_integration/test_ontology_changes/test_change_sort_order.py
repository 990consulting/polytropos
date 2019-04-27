import pytest

def test_change_sort_order_does_not_affect_path():
    """Changing a variable's sort order does not affect its path."""
    pytest.fail()

def test_change_sort_order_does_not_affect_parent():
    """Changing a variable's sort order does not change the parent's "children" property."""
    pytest.fail()

def test_change_sort_order_within_list_ok():
    """Moving a variable within its existing level is permitted, even in a list."""
    pytest.fail()

def test_change_sort_order_alters_json():
    """changing a variable's sort_order alters its json representation."""
    pytest.fail()

def test_change_sort_order_alters_tree():
    """changing a variable's sort_order alters the tree from the sort_order onward."""
    pytest.fail()

def test_sort_order_before_pushes_down():
    """Placing a variable before other variables pushes all those other variables down."""
    pytest.fail()

def test_sort_order_after_pulls_up():
    """Placing a variable after other variables pulls all those other variables up."""
    pytest.fail()

def test_negative_sort_order_raises():
    """Setting a sort order below zero is illegal."""
    pytest.fail()

def test_sort_order_gt_num_vars_raises():
    """Setting a sort order higher than the highest variable index is illegal."""
    pytest.fail()
