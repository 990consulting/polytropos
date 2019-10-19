from typing import Callable, Dict

import pytest


@pytest.fixture(scope="module")
def half_spec() -> Callable:
    def _half_spec(area: str, cardinal: int, ordinal: str, prefix: str, track_name: str, data_type: str = "Text") -> Dict:
        name_prefix = ""
        if area == "source":
            name_prefix = "source_"

        return {
            "%s_%s_folder_%i" % (area, prefix, cardinal): {
                "name": "%s%s_%s_folder" % (name_prefix, ordinal, track_name),
                "data_type": "Folder",
                "sort_order": 0
            },
            "%s_%s_folder_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_1" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_folder_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_folder_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_2" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_folder_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_list_%i" % (area, prefix, cardinal): {
                "name": "%sa_list" % name_prefix,
                "data_type": "List",
                "parent": "%s_%s_folder_%i" % (area, prefix, cardinal),
                "sort_order": 1
            },
            "%s_%s_list_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_1" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_list_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_2" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_keyed_list_%i" % (area, prefix, cardinal): {
                "name": "%sa_keyed_list" % name_prefix,
                "data_type": "KeyedList",
                "parent": "%s_%s_list_%i" % (area, prefix, cardinal),
                "sort_order": 1
            },
            "%s_%s_keyed_list_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_1" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_keyed_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_keyed_list_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_2" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_keyed_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_root_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%s%s_root_%s_%i_1" % (name_prefix, track_name, data_type.lower(), cardinal),
                "data_type": data_type,
                "sort_order": 1
            },
            "%s_%s_root_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%s%s_root_%s_%i_2" % (name_prefix, track_name, data_type.lower(), cardinal),
                "data_type": data_type,
                "sort_order": 1
            }
        }
    return _half_spec
