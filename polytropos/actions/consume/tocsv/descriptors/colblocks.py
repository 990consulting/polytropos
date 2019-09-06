from typing import List, Tuple, Optional, Iterator, Union, Dict

class DescriptorBlockToColumnBlocks:
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
        if 'type' in inner_item and inner_item['type'] in ('List', 'KeyedList'):
            if 'children' in inner_item:
                yield tuple(self._convert_list(inner_item['children'], inner_key))
            else:
                yield (inner_key,)
        else:
            raise ValueError('Unrecognized structure of the descriptor: a dict must be marked with '
                             'type List or KeyedList')