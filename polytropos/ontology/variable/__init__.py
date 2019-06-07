from dacite import from_dict
import polytropos.ontology.variable.__variable
from polytropos.ontology.variable.__variable import (
    Variable, Folder, List, NamedList, Primitive, Container, GenericList,
    Validator, Text, Decimal, Integer, Binary
)


def build_variable(data):
    data_type = data['data_type']
    cls = getattr(polytropos.ontology.variable.__variable, data_type)
    return from_dict(cls, data)
