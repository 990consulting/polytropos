from dataclasses import dataclass

# TODO See if these can be imported directly from Evolve
from polytropos.actions.evolve.__change import Change
from polytropos.actions.evolve.__lookup import lookup
from polytropos.actions.evolve.__subject import SubjectValidator
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Text


@lookup('color_names')
@dataclass
class ColorNameToRGB(Change):
    """Look up the RGB value for the color name specified by color_name_var, and store it in rgb_var."""
    color_name_var: Text = SubjectValidator(data_type=Text)
    rgb_var: Text = SubjectValidator(data_type=Text)

    def __call__(self, composite: Composite):
        # IRL, you'd have to handle nulls, decide how to deal with temporal variables, etc.
        color_name = composite.get_immutable(self.color_name_var.var_id)

        # At some point, I'll write a fancy retrieval/validation/assignment system, but that's not for the MVP
        rgb_value = self.lookups["color_names"][color_name]
        composite.put_immutable(self.rgb_var.var_id, rgb_value)
