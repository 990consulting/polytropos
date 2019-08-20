from dataclasses import dataclass
from typing import List, Tuple, Optional, Iterator, Union

from polytropos.ontology.schema import Schema

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
                # TODO what to do with multiple items in a dict?
                for inner_key, inner_item in item.items(): # type: str, Union[str, dict]
                    if isinstance(inner_item, str):
                        # If a list item is a dictionary with a single key-value pair, then the key is the actual data
                        # to be put in the column and the value is the name of the column
                        # TODO check that the item is the only thing in the dict
                        yield inner_key
                    elif isinstance(inner_item, dict):
                        if 'type' in inner_item and inner_item['type'] in ('List', 'NamedList'):
                            if 'children' in inner_item:
                                yield tuple(self._convert_list(inner_item['children'], inner_key))
                            else:
                                yield (inner_key,)
                        else:
                            raise Exception('Unrecognized structure of the descriptor: a dict must be marked with '
                                            'type List or NamedList')
                    else:
                        raise Exception("Unrecognized structure of the descriptor: can't convert an item of type " + type(inner_item))
            else:
                # TODO should test the handling of unknown types
                raise Exception("Unrecognized structure of the descriptor: can't convert an item of type " + type(item))

@dataclass
class DescriptorsToColumnNames:
    """Convert a list of column descriptors to column names. By default, the column names are the absolute path of the
    variables, but these column names can be overridden."""

    schema: Schema

    def __call__(self, descriptors: List) -> Tuple:
        """NOTE FOR FREELANCER:

        The YAML supplied in the tests contains variable IDs (eg., "i_outer_nested_named_list.") To convert this into
        the "absolute path" required for the task, call

            self.schema.get(var_id).absolute_path

        where "var_id" is the variable ID whose path you want.
        
        Schema.get:
        https://github.com/borenstein/polytropos/blob/csv/polytropos/ontology/schema.py#L138
        
        Variable.absolute_path:
        https://github.com/borenstein/polytropos/blob/csv/polytropos/ontology/variable/__variable.py#L227
        """
        pass
