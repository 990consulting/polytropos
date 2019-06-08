from dataclasses import dataclass
from typing import Dict, Optional, Any

from polytropos.actions.evolve import Change
from polytropos.ontology.variable import Text, Decimal, Variable
from polytropos.actions.evolve import SubjectValidator
from polytropos.util import nesteddicts

def get_value(composite: Dict, invariant_variable: Variable) -> Optional[Any]:
    path = ["invariant"] + list(invariant_variable.absolute_path)
    value = nesteddicts.get(composite, path)
    return value

@dataclass
class GeneratePersonDescription(Change):
    color_name_var: Text = SubjectValidator(data_type=Text)
    rgb_var: Text = SubjectValidator(data_type=Text)
    person_name_var: Text = SubjectValidator(data_type=Text)
    gender_var: Text = SubjectValidator(data_type=Text)
    weight_gain_var: Decimal = SubjectValidator(data_type=Decimal)
    sentence_var: Text = SubjectValidator(data_type=Text)

    def get_pronoun(self, composite: Dict):
        gender: str = get_value(composite, self.gender_var)

        pronoun_mapping = {
            "male": "he",
            "female": "she"
        }

        return pronoun_mapping[gender]

    def __call__(self, composite: Dict):
        template = "%s's favorite color is %s (%s). Over the observation period, %s gained %0.1f lbs."

        name = get_value(composite, self.person_name_var)
        color = get_value(composite, self.color_name_var)
        rgb = get_value(composite, self.rgb_var)
        weight_gain = get_value(composite, self.weight_gain_var)

        pronoun = self.get_pronoun(composite)

        sentence = template % (name, color, rgb, pronoun, weight_gain)
        print(self.sentence_var)
        sentence_path = ["invariant"] + list(self.sentence_var.absolute_path)
        nesteddicts.put(composite, sentence_path, sentence)
