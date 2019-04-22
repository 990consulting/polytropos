import etl4.ontology.variable.__variable
from etl4.ontology.variable.__variable import Variable
from dacite import from_dict


def build_variable(data):
    data_type = data['data_type']
    cls = getattr(etl4.ontology.variable.__variable, data_type)
    return from_dict(cls, data)
