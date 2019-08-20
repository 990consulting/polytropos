from dataclasses import dataclass
from typing import List, Tuple, Optional, Iterator, Union, Dict, cast

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable, VariableId
from polytropos.util import nesteddicts

class DescriptorsToBlocks:
    """Convert a list of column descriptors to column blocks, which can in turn be used to extract data."""
    def __call__(self, descriptors: List) -> Tuple:
        return tuple(self._convert_list(descriptors))

    def _convert_list(self, descriptors: List, list_name: Optional[str] = None) -> Iterator[Union[str, Tuple]]:
        """
        :param descriptors: A list of things to convert to a block
        :param list_name:   A name for the current sublist - if supplied, it's prepended to the converted list.
                            (It's done in the function to skip chaining the iterators when calling the function.)
        """
        if list_name is not None:
            yield list_name

        for item in descriptors: # type: Union[str, dict]
            if isinstance(item, str):
                yield item
            elif isinstance(item, dict):
                yield from self._handle_complex(item)
            else:
                # TODO should test the handling of unknown types
                raise ValueError("Unrecognized structure of the descriptor: can't convert an item of type "
                                 + type(item).__name__)

    def _handle_complex(self, item: Dict) -> Iterator[Union[str, Tuple]]:
        # TODO what to do with multiple items in a dict?
        for inner_key, inner_item in item.items():  # type: str, Union[str, dict]
            if isinstance(inner_item, str):
                # If a list item is a dictionary with a single key-value pair, then the key is the actual data
                # to be put in the column and the value is the name of the column
                # TODO check that the item is the only thing in the dict
                yield inner_key
            elif isinstance(inner_item, dict):
                yield from self._handle_nested(inner_item, inner_key)
            else:
                raise ValueError("Unrecognized structure of the descriptor: can't convert an item of type "
                                 + type(inner_item).__name__)

    def _handle_nested(self, inner_item: Dict, inner_key: str) -> Iterator[Union[str, Tuple]]:
        if 'type' in inner_item and inner_item['type'] in ('List', 'NamedList'):
            if 'children' in inner_item:
                yield tuple(self._convert_list(inner_item['children'], inner_key))
            else:
                yield (inner_key,)
        else:
            raise ValueError('Unrecognized structure of the descriptor: a dict must be marked with '
                             'type List or NamedList')

@dataclass
class DescriptorsToColumnNames:
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
        if ctype not in {"List", "NamedList"}:
            raise ValueError('Unexpected type specification "%s"' % ctype)

        variable: Variable = self.schema.get(var_id)
        if variable is None:
            raise ValueError('Unrecognized variable ID "%s"' % var_id)
        if variable.data_type != ctype:
            raise ValueError('%s root "%s" is actually a %s' % (ctype, var_id, variable.data_type))

        if ctype == "NamedList":
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
