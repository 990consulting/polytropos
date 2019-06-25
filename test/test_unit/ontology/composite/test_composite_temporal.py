from typing import Dict, Optional, Any

import pytest
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema

@pytest.fixture
def imperfect_composite(simple_schema: Schema) -> Composite:
    return Composite(simple_schema, {
        "2010": {
            "weight_in_pounds": None
        },
        "2011": {
            "weight_in_pounds": 170.1
        },
        "2012": {}
    })

def test_periods(simple_composite: Composite):
    assert set(simple_composite.periods) == {"2013", "2010", "2011", "2012"}

def test_periods_invariant_only(simple_schema: Schema, simple_doc: Dict):
    doc: Dict = {"immutable": simple_doc["immutable"]}
    composite: Composite = Composite(simple_schema, doc)
    assert set(composite.periods) == set()

def test_periods_none(simple_schema: Schema):
    composite: Composite = Composite(simple_schema, {})
    assert set(composite.periods) == set()

def test_get_all_observations(simple_composite):
    expected: Dict = {
        "2013": 172.3,
        "2010": 168.4,
        "2011": 170.1,
        "2012": 174.2
    }
    actual: Dict = {}
    for period, observation in simple_composite.get_all_observations("the_weight_var"):
        actual[period] = observation
    assert actual == expected

def test_get_all_observations_none(simple_schema):
    composite: Composite = Composite(simple_schema, {
        "2010": {},
        "2011": {},
        "2012": {
            "weight_in_pounds": 174.2
        }
    })
    expected: Dict = {
        "2012": 174.2
    }
    actual: Dict = {}
    for period, observation in composite.get_all_observations("the_weight_var"):
        actual[period] = observation
    assert actual == expected

def test_get_all_observations_has_nulls(imperfect_composite):
    expected: Dict = {
        "2010": None,
        "2011": 170.1
    }
    actual: Dict = {}
    for period, observation in imperfect_composite.get_all_observations("the_weight_var"):
        actual[period] = observation
    assert actual == expected

def test_get_all_observations_unknown_var_raises(simple_composite):
    with pytest.raises(ValueError):
        list(simple_composite.get_all_observations("not_a_thing"))

def test_get_observation(simple_composite):
    assert simple_composite.get_observation("the_weight_var", "2012", 174.2)

def test_get_observation_missing_permissive(imperfect_composite):
    actual: Optional[Any] = imperfect_composite.get_observation("the_weight_var", "2012", treat_missing_as_null=True)
    assert actual is None

def test_get_observation_missing_strict_raises(imperfect_composite):
    with pytest.raises(ValueError):
        imperfect_composite.get_observation("the_weight_var", "2012")

def test_get_observation_none(imperfect_composite):
    actual: Optional[Any] = imperfect_composite.get_observation("the_weight_var", "2010")
    assert actual is None

def test_get_observation_unknown_period_raises(imperfect_composite):
    with pytest.raises(ValueError):
        imperfect_composite.get_observation("the_weight_var", "2013")

def test_get_observation_unknown_var_raises(imperfect_composite):
    with pytest.raises(ValueError):
        imperfect_composite.get_observation("not_a_thing", "2012")

def test_put_observation(imperfect_composite):
    imperfect_composite.put_observation("the_weight_var", "2012", 190.1)
    assert imperfect_composite.content["2012"]["weight_in_pounds"] == 190.1

def test_put_observation_overwrites(imperfect_composite):
    imperfect_composite.put_observation("the_weight_var", "2011", 190.1)
    assert imperfect_composite.content["2011"]["weight_in_pounds"] == 190.1

def test_put_observation_creates_period(imperfect_composite):
    imperfect_composite.put_observation("the_weight_var", "2013", 190.1)
    assert imperfect_composite.content["2013"]["weight_in_pounds"] == 190.1

def test_put_observation_unknown_var_raises(imperfect_composite):
    with pytest.raises(ValueError):
        imperfect_composite.put_observation("not_a_thing", "2012", 190.1)
