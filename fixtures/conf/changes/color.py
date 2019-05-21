from typing import Dict

from etl4.ontology.metamorphosis.__change import Change
from etl4.ontology.metamorphosis.__lookup import lookup
from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.schema import Schema

class Rgb2Hsl(Change):
    """Get the RGB value at the location specified by rgb_var, convert it to HSL, and then store it in hsl_var."""

    @subject("rgb_var", data_types={"text"}, temporal=1)
    @subject("hsl_var", data_types={"text"}, temporal=1)
    def __init__(self, schema: Schema, lookups: Dict, rgb_var: str, hsl_var: str):
        super().__init__(schema, lookups, rgb_var, hsl_var)

    def __call__(self, composite: Dict):
        pass

class ColorNameToRGB(Change):
    """Look up the RGB value for the color name specified by color_name_var, and store it in rgb_var."""

    @lookup("color_names")
    @subject("color_name_var", data_types={"text"}, temporal=1)
    @subject("rgb_var", data_types={"text"}, temporal=1)
    def __init__(self, schema: Schema, lookups: Dict, color_name_var, rgb_var: str):
        super().__init__(schema, lookups, color_name_var, rgb_var)
