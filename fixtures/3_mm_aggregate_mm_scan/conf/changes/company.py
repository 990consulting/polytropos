from dataclasses import dataclass
from typing import Dict

from polytropos.actions.evolve.__change import Change
from polytropos.ontology.variable import Variable
from polytropos.util import composites

@dataclass
class AssignCityState(Change):
    # TODO: Validation
    zip_var: Variable
    city_var: Variable
    state_var: Variable

    def __call__(self, composite: Dict):
        zip_code: str = composites.get_property(composite, self.zip_var)

        city = self.lookups["zipcodes"][zip_code]["City"]
        composites.put_property(composite, self.city_var, city)

        state = self.lookups["zipcodes"][zip_code]["State"]
        composites.put_property(composite, self.state_var, state)
