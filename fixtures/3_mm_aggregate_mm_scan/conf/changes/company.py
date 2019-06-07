from dataclasses import dataclass
from typing import Dict

from etl4.ontology.metamorphosis import Change
from etl4.ontology.schema import Schema
from etl4.ontology.variable import Variable
from etl4.util import composites

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
