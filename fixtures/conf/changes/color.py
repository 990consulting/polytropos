from dataclasses import dataclass
from typing import Dict
from etl4.ontology.metamorphosis.__change import Change
from etl4.ontology.metamorphosis.__lookup import lookup
from etl4.ontology.metamorphosis.__subject import SubjectValidator
from etl4.ontology.schema import Schema
from etl4.ontology.variable import Variable, Text
from etl4.util import nesteddicts


@dataclass
class ColorNameToRGB(Change):
    """Look up the RGB value for the color name specified by color_name_var, and store it in rgb_var."""
    color_name_var: Text = SubjectValidator(data_type=Text)
    rgb_var: Text = SubjectValidator(data_type=Text)

    # @lookup("color_names")

    def __call__(self, composite: Dict):
        # IRL, you'd have to handle nulls, decide how to deal with temporal variables, etc.
        color_name_path = ["invariant"] + list(self.color_name_var.absolute_path)
        color_name = nesteddicts.get(composite, color_name_path)

        # At some point, I'll write a fancy retrieval/validation/assignment system, but that's not for the MVP
        rgb_value = self.lookups["color_names"][color_name]
        rgb_path = ["invariant"] + list(self.rgb_var.absolute_path)
        nesteddicts.put(composite, rgb_path, rgb_value)

