from dataclasses import dataclass
from typing import Dict

from polytropos.actions.filter import Filter
from polytropos.actions.evolve import SubjectValidator
from polytropos.ontology.variable.__variable import Binary
from polytropos.util import composites

@dataclass
class RetainOnlyFemales(Filter):
    male_flag: Binary = SubjectValidator(data_type=Binary)

    def passes(self, composite: Dict) -> bool:
        male: bool = composites.get_property(composite, self.male_flag)
        return not male
