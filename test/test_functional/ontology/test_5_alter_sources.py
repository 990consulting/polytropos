from typing import Dict, List
import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable, VariableId


def test_alter_source_raises(target_nested_dict_track):
    track: Track = target_nested_dict_track
    var: Variable = track[VariableId("target_var_2")]
    with pytest.raises(AttributeError):
        var.sources = ["source_var_2", "source_var_3"]
