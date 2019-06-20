from dataclasses import dataclass

from polytropos.actions.evolve.__change import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Text, Decimal
from polytropos.actions.validator import VariableValidator

@dataclass
class GeneratePersonDescription(Change):
    color_name_var: str = VariableValidator(data_type=Text)
    rgb_var: str = VariableValidator(data_type=Text)
    person_name_var: str = VariableValidator(data_type=Text)
    gender_var: str = VariableValidator(data_type=Text)
    weight_gain_var: str = VariableValidator(data_type=Decimal)
    sentence_var: str = VariableValidator(data_type=Text)

    def get_pronoun(self, composite: Composite):
        gender: str = composite.get_immutable(self.gender_var)

        pronoun_mapping = {
            "male": "he",
            "female": "she"
        }

        return pronoun_mapping[gender]

    def __call__(self, composite: Composite):
        template = "%s's favorite color is %s (%s). Over the observation period, %s gained %0.1f lbs."

        name: str = composite.get_immutable(self.person_name_var)
        color: str = composite.get_immutable(self.color_name_var)
        rgb: str = composite.get_immutable(self.rgb_var)
        weight_gain: float = composite.get_immutable(self.weight_gain_var)

        pronoun = self.get_pronoun(composite)

        sentence = template % (name, color, rgb, pronoun, weight_gain)
        composite.put_immutable(self.sentence_var, sentence)
