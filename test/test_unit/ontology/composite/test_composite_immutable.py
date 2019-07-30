from typing import Optional, Dict

import pytest
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema

def test_get_immutable(simple_composite: Composite):
    expected: str = "FFA000"
    actual: str = simple_composite.get_immutable("the_rgb_var")
    assert actual == expected

def test_get_immutable_missing_permissive(simple_schema: Schema):
    composite: Composite = Composite(simple_schema, {})
    actual: Optional[str] = composite.get_immutable("the_rgb_var", treat_missing_as_null=True)
    assert actual is None

def test_get_immutable_missing_strict_raises(simple_schema: Schema):
    composite: Composite = Composite(simple_schema, {})
    with pytest.raises(ValueError):
        composite.get_immutable("the_rgb_var")

def test_get_immutable_null(simple_schema: Schema):
    composite: Composite = Composite(simple_schema, {
        "immutable": {
            "first_name": None
        }
    })
    actual: Optional[str] = composite.get_immutable("the_person_name_var")
    assert actual is None

@pytest.mark.parametrize("permissive", [True, False])
def test_get_immutable_unknown_var_raises(simple_composite, permissive):
    with pytest.raises(ValueError):
        simple_composite.get_immutable("not_a_thing", treat_missing_as_null=permissive)

def test_put_immutable(simple_schema: Schema):
    composite: Composite = Composite(simple_schema, {})
    composite.put_immutable("the_rgb_var", "F0F0F0")
    expected: Dict = {
        "immutable": {
            "color_info": {
                "rgb_value": "F0F0F0"
            }
        }
    }
    actual = composite.content
    assert actual == expected

def test_put_immutable_overwrites(simple_composite: Composite):
    simple_composite.put_immutable("the_rgb_var", "F0F0F0")
    expected = "F0F0F0"
    actual = simple_composite.content["immutable"]["color_info"]["rgb_value"]
    assert actual == expected

def test_put_immutable_unknown_var_raises(simple_composite):
    with pytest.raises(ValueError):
        simple_composite.put_immutable("not_a_thing", "xyz")

def test_del_immutable(simple_composite: Composite):
    expected: Dict = {
        "first_name": "Steve",
        "gender": "male",
        "total_weight_gain": 3.9,
        "personal_summary": "Steve's favorite color is orange (FFA000). Over the observation period, he gained"
                            " 3.9 lbs."
    }
    simple_composite.del_immutable("color_folder")
    assert simple_composite.content["immutable"] == expected
