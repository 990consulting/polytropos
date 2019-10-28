from dataclasses import dataclass
from typing import List, Dict, Union, Iterator

from polytropos.util import nesteddicts

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId, Variable
from polytropos.util.nesteddicts import MissingDataError

def _elements_of(content: Union[List, Dict]) -> Iterator[Dict]:
    if isinstance(content, Dict):
        yield from content.values()
    else:
        yield from content

@dataclass
class Delete(Change):
    """Deletes all instances of specified variables from each composite. Currently does not handle variables inside of
    nested lists. However, it does handle variables inside lists or keyed lists, and can handle either temporal or
    immutable variables."""
    targets: List[VariableId]

    def delete_multiple(self, var: Variable, period_content: Dict) -> None:
        list_base_var: Variable = self.schema.get(var.nearest_list)
        assert not list_base_var.descends_from_list, "Nested list handling not implemented"
        try:
            content: Union[Dict, List] = nesteddicts.get(period_content, list_base_var.absolute_path)
            if content is None:
                return
        except MissingDataError:
            return

        for element in _elements_of(content):  # type: Dict
            try:
                nesteddicts.delete(element, var.relative_path)
            except MissingDataError:
                continue

    def delete_immutable(self, var: Variable, composite: Composite) -> None:
        if "immutable" not in composite.content:
            return

        if var.descends_from_list:
            self.delete_multiple(var, composite.content["immutable"])
        else:
            composite.del_immutable(var.var_id)

    def delete_temporal(self, var: Variable, composite: Composite) -> None:
        for period in composite.periods:
            if var.descends_from_list:
                self.delete_multiple(var, composite.content[period])
            else:
                composite.del_observation(var.var_id, period)

    def __post_init__(self) -> None:
        self.target_vars: List[Variable] = [self.schema.get(target) for target in self.targets]
        for var_id, var in zip(self.targets, self.target_vars):
            if var is None:
                raise ValueError('Unknown variable "%s"' % var_id)

    def __call__(self, composite: Composite) -> None:
        for var_id, var in zip(self.targets, self.target_vars):
            if var.temporal:
                self.delete_temporal(var, composite)
            else:
                self.delete_immutable(var, composite)
