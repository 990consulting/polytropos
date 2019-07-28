import os
import json
from collections import defaultdict
from typing import Dict, Optional

def _repair_spec(track_spec: Dict[str, Dict]) -> None:
    parents: Dict[str, Dict] = defaultdict(dict)

    for var_id, variable in track_spec.items():
        parent: Optional[str] = variable.get("parent")
        parents[parent][var_id] = variable

    for parent_id, children in parents.items():
        child_names: Dict[str] = {}
        for child_id, child in children.items():
            name: str = child["name"]
            assert name not in child_names
            child_names[name] = child_id
        sort_order: int = 0
        for child_name, child_id in sorted(zip(child_names.keys(), child_names.values())):
            track_spec[child_id]["sort_order"] = sort_order
            sort_order += 1

def _repair_track_sort_order(schema_location: str, track_name: str):
    track_fn: str = os.path.join(schema_location, track_name + ".json")
    with open(track_fn) as fh:
        track_spec: Dict = json.load(fh)

    _repair_spec(track_spec)

    repaired_fn: str = os.path.join(schema_location, track_name + "_repaired.json")
    with open(repaired_fn, "w") as fh:
        json.dump(track_spec, fh, indent=2)

def repair_sort_order(schema_location: str):
    """Replaces the existing sort order in a schema (if any) with an arbitrary, but valid, sort order. No aspect of the
    old sort order will be preserved; the new order will be alphabetized by variable name."""
    for track_name in ["temporal", "immutable"]:
        _repair_track_sort_order(schema_location, track_name)
