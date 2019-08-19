from dataclasses import dataclass

from polytropos.ontology.composite import Composite

from polytropos.actions.evolve.__change import Change
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.variable import Text, VariableId


@dataclass
class AssignCityState(Change):
    zip_var: VariableId = VariableValidator(data_type=Text, temporal=-1)
    city_var: VariableId = VariableValidator(data_type=Text, temporal=-1)
    state_var: VariableId = VariableValidator(data_type=Text, temporal=-1)

    def __call__(self, composite: Composite):
        zip_code: str = composite.get_immutable(self.zip_var)

        city = self.lookups["zipcodes"][zip_code]["City"]
        composite.put_immutable(self.city_var, city)

        state = self.lookups["zipcodes"][zip_code]["State"]
        composite.put_immutable(self.state_var, state)
