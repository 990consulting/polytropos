from typing import Dict, Iterable, List

from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change

def _handle_list(the_list: List) -> None:
    for item in the_list:
        if isinstance(item, Dict):
            _depth_first_prune(item)

def _depth_first_prune(content: Dict) -> None:
    keys: List[str] = [key for key in content.keys()]  # Prevent errors from modifying during iteration
    for key in keys:
        value = content[key]

        if value is None:
            del content[key]
            continue

        # Perform depth-first prune
        if isinstance(value, dict):
            _depth_first_prune(value)
        elif isinstance(value, list):
            _handle_list(value)

        # If, at this point, the value is an empty list or dict, get rid of it
        if value in [{}, []]:
            del content[key]

class Prune(Change):
    """Perform a depth-first search on each period (and Immutable). Within each, perform a depth first search that
    deletes all keys containing None, and empty list, or an empty dict. In this manner, a deeply nested structure of
    empty lists and dicts will be completely removed. Note that completely empty periods (including Immutable) will be
    removed as well."""

    def __call__(self, composite: Composite) -> None:
        _depth_first_prune(composite.content)