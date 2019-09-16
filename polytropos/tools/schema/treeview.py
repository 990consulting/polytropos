from collections import OrderedDict
from typing import Dict, Any, Iterable, Optional

from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_DOUBLE
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

def _traverse(variables: Iterable[Variable]) -> Dict:
    unsorted: Dict[str, Any] = {}
    sort_orders: Dict[str, int] = {}

    for var in variables:
        if var.data_type in {"Folder", "List", "KeyedList"}:
            value: Dict = _traverse(var.children)
        else:
            value = {}
        key: str = "%i %s (%s | %s)" % (var.sort_order, var.name, var.data_type, var.var_id)
        unsorted[key] = value
        sort_orders[key] = var.sort_order

    # Python Cookbook, recipe 1.8
    ret: OrderedDict[str, int] = OrderedDict()
    for sort_order, key in sorted(zip(sort_orders.values(), sort_orders.keys())):
        ret[key] = unsorted[key]

    return ret

def _process_track(track: Track) -> Dict:
    if len(track) == 0:
        return {}

    return _traverse(track.roots)

def _track_to_tree(root_name: str, track: Track) -> str:
    rooted_tree: Dict = {root_name: _process_track(track)}
    box_tr: LeftAligned = LeftAligned(draw=BoxStyle(gfx=BOX_DOUBLE, horiz_len=1, indent=1))
    return box_tr(rooted_tree)

def as_ascii(schema: Schema) -> str:
    temporal: str = _track_to_tree("temporal", schema.temporal)
    immutable: str = _track_to_tree("immutable", schema.immutable)
    return "\n\n".join([temporal, immutable])

def print_from_files(schema_basepath: str, schema_name: str) -> None:
    schema: Optional[Schema] = Schema.load(schema_name, schema_basepath)
    assert schema is not None
    tree: str = as_ascii(schema)
    print(tree)