from typing import Dict, Optional, Any, Iterator, Tuple, List
from etl4.util import nesteddicts

from etl4.ontology.variable import Variable

def get_periods(composite: Dict) -> Iterator[str]:
    """Iterate over all of the observation periods contained in this composite."""
    yield from set(composite.keys()) - {"invariant"}

# TODO Check to verify that the variable is indeed invariant
# TODO Check that this isn't trying to grab a list descendant
def get_property(composite: Dict, prop: Variable) -> Optional[Any]:
    """Get an invariant "variable" (property) from this composite."""
    path = ["invariant"] + list(prop.absolute_path)
    return nesteddicts.get(composite, path)

# TODO Check to verify that the variable is indeed temporal
# TODO Check that this isn't trying to grab a list descendant
def get_all_observations(composite: Dict, variable: Variable) -> Iterator[Tuple[str, Any]]:
    """Iterate over all observations of a temporal variable from this composite."""
    var_path: List = list(variable.absolute_path)
    for period in get_periods(composite):
        yield period, nesteddicts.get(composite, [period] + var_path)

# TODO Check to verify that the variable is indeed temporal
# TODO Check that this isn't trying to grab a list descendant
def get_observation(composite: Dict, period: str, variable: Variable, treat_missing_as_null=False) -> Optional[Any]:
    """Get the value of a temporal variable for a particular observation period."""
    path: List = [period] + list(variable.absolute_path)
    return nesteddicts.get(composite, path)

# TODO Add validation of value against variable type
# TODO Check to verify that the variable is indeed invariant
# TODO Check that this isn't trying to populate a list descendant
def put_property(composite: Dict, prop: Variable, value: Optional[Any]) -> None:
    """Assign (or overwrite) a value to an invariant "variable" (property) in this composite."""
    path: List = ["invariant"] + list(prop.absolute_path)
    nesteddicts.put(composite, path, value)

# TODO Add validation of value against variable type
# TODO Check to verify that the variable is indeed temporal
# TODO Check that this isn't trying to populate a list descendant
def put_observation(composite: Dict, period: str, variable: Variable, value: Optional[Any]) -> None:
    """Assign (or overwrite) the value of a variable into a particular observation."""
    path: List = [period] + list(variable.absolute_path)
    nesteddicts.put(composite, path, value)