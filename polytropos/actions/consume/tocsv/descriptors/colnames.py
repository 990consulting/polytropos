from dataclasses import dataclass
from typing import Dict, Iterator, Union, List

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable, VariableId
from polytropos.util import nesteddicts

@dataclass
class DescriptorBlockToColumnNames:
    """Convert a list of column descriptors to column names. By default, the column names are the absolute path of the
    variables, but these column names can be overridden."""

    schema: Schema

    def _var_path(self, var_id: str) -> str:
        var: Variable = self.schema.get(var_id)
        if var is None:
            raise ValueError('Unrecognized variable id "%s"' % var_id)
        return nesteddicts.path_to_str(var.absolute_path)

    def _nested_case(self, descriptor: Dict) -> Iterator[str]:
        var_id: VariableId = list(descriptor.keys())[0]
        content: Dict = list(descriptor.values())[0]

        if "type" not in content:
            raise ValueError("Expected type specification for nested columns")
        ctype: str = content["type"]
        if ctype not in {"List", "KeyedList"}:
            raise ValueError('Unexpected type specification "%s"' % ctype)

        variable: Variable = self.schema.get(var_id)
        if variable is None:
            raise ValueError('Unrecognized variable ID "%s"' % var_id)
        if variable.data_type != ctype:
            raise ValueError('%s root "%s" is actually a %s' % (ctype, var_id, variable.data_type))

        if ctype == "KeyedList":
            if "key_column_name" in content:
                yield content["key_column_name"]
            else:
                yield nesteddicts.path_to_str(variable.absolute_path)
        if "children" in content:
            yield from self(content["children"])

    def _complex_case(self, descriptor: Dict) -> Iterator[str]:
        assert len(descriptor) == 1
        content: Union[str, Dict] = list(descriptor.values())[0]

        # If the descriptor is just {var_id: some_text} then "some_text" is the column label
        if isinstance(content, str):
            yield content
        else:
            yield from self._nested_case(descriptor)

    def __call__(self, descriptors: List) -> Iterator[str]:
        for descriptor in descriptors:
            if isinstance(descriptor, str):
                yield self._var_path(descriptor)
            elif isinstance(descriptor, Dict):
                yield from self._complex_case(descriptor)