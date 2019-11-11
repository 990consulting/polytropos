from collections import Callable
from typing import Dict

import pytest

@pytest.fixture()
def make_spec() -> Callable:
    def _make_spec() -> Dict:
        ret: Dict = {
            "source": {
                "name": "phone",
                "data_type": "Phone",
                "sort_order": 0
            },
            "target": {
                "name": "the_target",
                "data_type": "Text",
                "sort_order": 1
            }
        }
        return ret

    return _make_spec

