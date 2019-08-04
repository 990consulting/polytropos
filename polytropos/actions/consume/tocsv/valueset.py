from typing import Dict, Optional, Any, List

from attr import dataclass

@dataclass
class ValueSet:

    # A dictionary with an element for every temporal singleton column defined, with var_id as key.
    singleton_values: Dict[str, Optional[Any]]

    # A dictionary with an element for every temporal list, where the list root is the key and the value is a list of
    # dictionaries of child variable IDs to values. Nested lists are counted as a single list.
    list_values: Dict[str, List[Dict[str, Optional[Any]]]]

    # Returns a dictionary with an element for every temporal named list, where the list root is the key and the
    # value is a dictionary of child variable IDs to values. Nested named lists are counted as a single named list.
    named_list_values: Dict[str, Dict[str, Dict[str, Optional[Any]]]]

    def merge(self, other: "ValueSet") -> "ValueSet":
        """Combines this and another ValueSet into a new ValueSet."""
        pass