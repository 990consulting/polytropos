from typing import Dict, Optional, Any

from etl4.ontology.metamorphosis.__change import Change
from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.schema import Schema
from etl4.ontology.variable import Variable
from etl4.util import nesteddicts

def get_value(composite: Dict, invariant_variable: Variable) -> Optional[Any]:
    path = ["invariant"] + list(invariant_variable.absolute_path)
    value = nesteddicts.get(composite, path)
    return value

class GeneratePersonDescription(Change):

    @subject("color_name_var", data_types={"Text"}, temporal=-1)
    @subject("rgb_var", data_types={"Text"}, temporal=-1)
    @subject("person_name_var", data_types={"Text"}, temporal=-1)
    @subject("gender_var", data_types={"Text"}, temporal=-1)
    @subject("weight_gain_var", data_types={"Decimal"}, temporal=-1)
    @subject("sentence_var", data_types={"Text"}, temporal=-1)
    def __init__(self, schema: Schema, lookups: Dict, color_name_var, rgb_var, person_name_var, gender_var,
                 weight_gain_var, sentence_var):
        super().__init__(schema, lookups, color_name_var, rgb_var, person_name_var, gender_var, weight_gain_var,
                         sentence_var)

        self.color_name_var = color_name_var
        self.rgb_var = rgb_var
        self.person_name_var = person_name_var
        self.gender_var = gender_var
        self.weight_gain_var = weight_gain_var
        self.sentence_var = sentence_var

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
