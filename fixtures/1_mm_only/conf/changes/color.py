from dataclasses import dataclass
from typing import Dict

# TODO See if these can be imported directly from metamorphosis
from polytropos.actions.evolve import Change
from polytropos.actions.evolve import lookup
from polytropos.actions.evolve import SubjectValidator
from polytropos.ontology.variable import Text
from polytropos.util import nesteddicts


@lookup('color_names')
@dataclass
class ColorNameToRGB(Change):
    """Look up the RGB value for the color name specified by color_name_var, and store it in rgb_var."""
    color_name_var: Text = SubjectValidator(data_type=Text)
    rgb_var: Text = SubjectValidator(data_type=Text)

    def __call__(self, composite: Dict):
        # IRL, you'd have to handle nulls, decide how to deal with temporal variables, etc.
        color_name_path = ["invariant"] + list(self.color_name_var.absolute_path)
        color_name = nesteddicts.get(composite, color_name_path)

        # At some point, I'll write a fancy retrieval/validation/assignment system, but that's not for the MVP
        rgb_value = self.lookups["color_names"][color_name]
        rgb_path = ["invariant"] + list(self.rgb_var.absolute_path)
        nesteddicts.put(composite, rgb_path, rgb_value)

