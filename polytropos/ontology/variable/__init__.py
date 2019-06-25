from dacite import from_dict  # dacite turns dictionaries into data classes
import polytropos.ontology.variable.__variable
from polytropos.ontology.variable.__variable import (
    Variable, Folder, List, NamedList, Primitive, Container, GenericList,
    Validator, Text, Decimal, Integer, Binary
)


def build_variable(data):
    data_type = data['data_type']
    try:
        cls = getattr(polytropos.ontology.variable.__variable, data_type)
        return from_dict(cls, data)
    except Exception as e:
        print("breakpoint")
        raise e
