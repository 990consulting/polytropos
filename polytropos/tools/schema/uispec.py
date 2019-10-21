from typing import List, Dict, Optional

class GUITreeToSpec:
    """Converts a tree from the Polytropos user interface into a Polytropos specification file."""
    def __init__(self, tree_spec: List[Dict]):
        self.tree_spec = tree_spec
        self.ret: Dict = {}

    def traverse(self, node: Dict, sort_order: int, parent_id: Optional[str] = None) -> None:
        var_id: str = node["varId"]
        if var_id == "example_1a":
            print("breakpoint")

        if var_id in self.ret:
            raise ValueError('Variable ID "{}" appears twice in schema'.format(var_id))

        assert var_id not in self.ret, 'Variable ID "%s" appears twice in '
        spec: Dict = {
            "name": node["title"],
            "data_type": node["dataType"],
            "sort_order": sort_order
        }
        if "metadata" in node and len(node["metadata"]) > 0:
            spec["metadata"] = node["metadata"]
        if "sources" in node and len(node["sources"]) > 0:
            spec["sources"] = node["sources"]
        if parent_id is not None:
            spec["parent"] = parent_id
        self.ret[var_id] = spec

        if "children" in node:
            for sort_order, child in enumerate(node["children"]):
                self.traverse(child, sort_order, parent_id=var_id)

    def __call__(self) -> Dict:
        self.ret = {}
        for sort_order, root in enumerate(self.tree_spec):
            self.traverse(root, sort_order)
        return self.ret
