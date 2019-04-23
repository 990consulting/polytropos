from addict import Dict as Addict
from dacite import from_dict
import etl4.ontology.variable.__variable
from etl4.ontology.variable.__variable import Variable, Folder, List, NamedList


def build_variable(data):
    data_type = data['data_type']
    cls = getattr(etl4.ontology.variable.__variable, data_type)
    if isinstance(data, Addict):
        # addict messes up with dataclasses default values
        data = data.to_dict()
    return from_dict(cls, data)
