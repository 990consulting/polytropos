import os
from abc import ABC
from collections import deque
from typing import Any, cast, List, Optional, Iterable, Deque

from polytropos.actions.filter.univariate.__univariate import UnivariateFilter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

def get_raw_values(values: Optional[List], file_name: Optional[str], clazz: str) -> Iterable[str]:
    if values is not None and file_name is not None:
        raise ValueError("You set both the 'file_name' and 'values' parameter for a {} filter. You can supply "
                         "matching values either in-line or in a file, but not both.".format(clazz))

    if values is not None and len(values) > 0:
        return values

    if file_name is not None and not os.path.exists(file_name):
        abspath: str = os.path.abspath(file_name)
        raise FileNotFoundError("Values file '{}' not found for {} filter.".format(abspath, clazz))

    if file_name is not None:
        abspath = os.path.abspath(file_name)
        file_vals: Deque[str] = deque()
        for line_num, line in enumerate(open(file_name)):
            value_from_file: str = line.strip()
            if value_from_file == "":
                raise ValueError("Empty line encountered at line {} of values file '{}' for {} filter."
                                 .format(line_num + 1, abspath, clazz))

            file_vals.append(value_from_file)

        if len(file_vals) == 0:
            raise ValueError("Empty values file '{}' for {} filter.".format(abspath, clazz))

        return file_vals

    raise ValueError('Must provide at least one matching value for "one-of" filters.')

class OneOfFilter(UnivariateFilter, ABC):
    def __init__(self, context: Context, schema: Schema, var_id: str, narrows: bool = True,
                 filters: bool = True, pass_condition: str = "any", values: Optional[List] = None,
                 file_name: Optional[str] = None):

        super(OneOfFilter, self).__init__(context, schema, var_id, narrows=narrows, filters=filters,
                                          pass_condition=pass_condition)

        raw_values: Iterable[str] = get_raw_values(values, file_name, self.__class__.__name__)

        self.values = {self.variable.cast(value) for value in raw_values}

        if self.variable.data_type == "Text":
            self.values = {cast(str, value).lower() for value in self.values}

    def _validate(self) -> None:
        """Check for any class-specific parameter requirements."""
        pass

    def missing_value_passes(self) -> bool:
        return False

class MatchesOneOf(OneOfFilter):
    def compares_true(self, candidate: Any) -> bool:
        return candidate in self.values

class ContainsOneOf(OneOfFilter):
    def _validate(self) -> None:
        pass

    def compares_true(self, candidate: str) -> bool:
        for value in self.values:
            v: str = cast(str, value)
            if v in candidate:
                return True
        return False
