import etl4.ontology.variable.__variable
from etl4.ontology.variable.__variable import Variable
from dacite import from_dict


def build(data_type, data):
    cls = getattr(etl4.ontology.variable.__variable, data_type)
    return from_dict(cls, data)
