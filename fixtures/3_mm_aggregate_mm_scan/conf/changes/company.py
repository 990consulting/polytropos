from typing import Dict

from etl4.ontology.metamorphosis import Change
from etl4.ontology.schema import Schema
from etl4.ontology.variable import Variable
from etl4.util import composites

class AssignCityState(Change):
    # Quimey -- I stubbed this constructor until I see what your constructor implementation looks like
    def __init__(self, schema: Schema, lookups: Dict, *subjects):
        super().__init__(schema, lookups, *subjects)
        self.zip_var: Variable = None
        self.city_var: Variable = None
        self.state_var: Variable = None

    def __call__(self, composite: Dict):
        zip_code: str = composites.get_property(composite, self.zip_var)

        city = self.lookups["zipcodes"][zip_code]["city"]
        composites.put_property(composite, self.city_var, city)

        state = self.lookups["zipcodes"][zip_code]["state"]
        composites.put_property(composite, self.state_var, state)
