from dataclasses import dataclass

from polytropos.actions.evolve.__change import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId


@dataclass
class AssignCityState(Change):
    zip_var: VariableId
    city_var: VariableId
    state_var: VariableId

    def __call__(self, composite: Composite):
        zip_code: str = composite.get_immutable(self.zip_var)

        city = self.lookups["zipcodes"][zip_code]["City"]
        composite.put_immutable(self.city_var, city)

        state = self.lookups["zipcodes"][zip_code]["State"]
        composite.put_immutable(self.state_var, state)
