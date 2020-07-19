import os
from typing import List, Dict

from polytropos.actions.evolve.__lookup import load_lookups

def test_load_lookups(basepath):
    fixture_dir: str = os.path.join(basepath, "test_unit", "action", "evolve", "lookup")
    requested: List[str] = ["lookup1", "lookup2"]

    expected: Dict[str, Dict] = {
        "lookup1": {
            "john": {
                "color": "blue"
            },
            "mary": {
                "color": "orange"
            }
        },
        "lookup2": {
            "x": {
                "foo": "1",
                "bar": "2"
            },
            "y": {
                "foo": "-2",
                "bar": "-4"
            }
        }
    }

    actual: Dict = load_lookups(requested, fixture_dir)
    assert actual == expected