from dacite import from_dict, Config  # dacite turns dictionaries into data classes
import polytropos.ontology.variable.__variable
from polytropos.ontology.variable.__variable import (
    Variable, Folder, List, NamedList, Primitive, Container, GenericList,
    Validator, Text, Decimal, Integer, Binary, VariableId,
    Unary, Currency, Phone, Email, URL, Date
)



