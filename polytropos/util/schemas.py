from typing import Dict, List, cast

from polytropos.ontology.variable import VariableId

def build_folders(target: Dict, path: List[str], name_prefix: str) -> VariableId:
    assert len(path) > 0
    cur: str = path[-1]
    cur_var_id: str = name_prefix + "_".join(path)

    if cur_var_id not in target:
        var_spec: Dict = {
            "name": cur,
            "data_type": "Folder"
        }
        if len(path) > 1:
            parent_id: str = build_folders(target, path[:-1], name_prefix)
            var_spec["parent"] = parent_id
        target[cur_var_id] = var_spec
    else:
        assert target[cur_var_id]["data_type"] in {"Folder", "List", "KeyedList"}
    return cast(VariableId, cur_var_id)
