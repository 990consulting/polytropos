from dacite import from_dict
import etl4.ontology.variable.__variable
from etl4.ontology.variable.__variable import (
    Variable, Folder, List, NamedList, Primitive, Container, GenericList,
    Validator, Text, Decimal
)


def build_variable(data):
    data_type = data['data_type']
    cls = getattr(etl4.ontology.variable.__variable, data_type)
    return from_dict(cls, data)
