from typing import Dict, Callable, Iterable, List, Set

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track
from polytropos.util import composites
import pytest

############
# Fixtures #
############

def empty_composite():
    return {}

def immutable_only_composite() -> Dict:
    return {
        "immutable": {
            "the_text": "foo",
            "the_nested_list": [
                {
                    "named_list": {
                        "A": {
                            "the_inner_value": 1
                        },
                        "B": {
                            "the_inner_value": 2
                        }
                    }
                }
            ]
        }
    }

def temporal_only_composite():
    return {
        "2011": {"the_decimal": 1.5},
        "2012": {"the_decimal": 2.5}
    }

def all_composite():
    immutable = immutable_only_composite()
    temporal = temporal_only_composite()
    return {**immutable, **temporal}

@pytest.fixture
def temporal_track() -> Track:
    spec: Dict = {
        "the_decimal_id": {
            "name": "the_decimal",
            "data_type": "Decimal",
            "sort_order": 0
        },
        "the_currency_id": {
            "name": "the_currency",
            "data_type": "Currency",
            "sort_order": 1
        }
    }
    return Track.build(spec, None, "temporal")

def immutable_track() -> Track:
    spec: Dict = {
        "the_text_id": {
            "name": "the_text",
            "data_type": "Text",
            "sort_order": 0
        },
        "outer_id": {
            "name": "the_nested_list",
        }
    }
    pass

@pytest.fixture
def schema(temporal_track, immutable_track) -> Schema:
    return Schema(temporal_track, immutable_track)

@pytest.fixture

@pytest.mark.parametrize("get_composite, expected", [
    (empty_composite, set()),
    (immutable_only_composite, set()),
    (temporal_only_composite, {"2011", "2012"}),
    (all_composite, {"2011", "2012"})
])
def test_get_periods(get_composite: Callable, expected: Set):
    composite: Dict = get_composite()
    actual: Set = set(composites.get_periods(composite))
    assert actual == expected

def test_get_property():
    pytest.fail()

def test_get_property_for_temporal_raises():
    pytest.fail()

def test_get_all_observations_empty():
    pytest.fail()

def test_get_all_observations():
    pytest.fail()

def test_get_all_observations_for_immutable_raises():
    pytest.fail()

def test_get_observation_missing_safe():
    pytest.fail()

def test_get_observation_missing_unsafe():
    pytest.fail()

def test_get_observation_null():
    pytest.fail()

def test_get_observation():
    pytest.fail()

def test_put_property():
    pytest.fail()

def test_put_property_null():
    pytest.fail()

def test_put_property_for_temporal_raises():
    pytest.fail()

def test_put_observation():
    pytest.fail()

def test_put_observation_null():
    pytest.fail()

def test_put_observation_for_immutable_raises():
    pytest.fail()

def test_encode_list_trivial_case():
    """Empty mappings dictionary, no content."""
    pytest.fail()

def test_encode_list_unexpected_key_raises():
    """A content dictionary containing keys not defined in the mappings raises."""
    pytest.fail()

def test_encode_list_missing_keys():
    """A content dictionary with missing keys simply does not populate the corresponding fields in the mappings."""
    pytest.fail()

def test_encode_list_single_item():
    """Standard case with a single list item in content"""
    pytest.fail()

def test_encode_list_multiple_items():
    """Standard case with more than one list item in content."""
    pytest.fail()

def test_encode_list_nested():
    """A case in which lists are nested, and encode_list must be run multiple times."""
    pytest.fail()