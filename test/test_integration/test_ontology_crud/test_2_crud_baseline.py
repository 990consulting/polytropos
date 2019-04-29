from etl4.ontology.variable import Variable

def test_has_targets_no(target_nested_dict_track):
    source_track = target_nested_dict_track.source
    source_var: Variable = source_track.variables["source_var_3"]
    assert not source_var.has_targets

def test_get_children_no_parents(target_nested_dict_track):
    source_track = target_nested_dict_track.source
    source_var: Variable = source_track.variables["source_folder_3"]
    assert [] == list(source_var.children)
