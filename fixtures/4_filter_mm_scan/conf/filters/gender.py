from dataclasses import dataclass
from typing import Dict

from polytropos.ontology.filter import Filter
from polytropos.ontology.metamorphosis.__subject import SubjectValidator
from polytropos.ontology.variable.__variable import Binary
from polytropos.util import composites

@dataclass
class RetainOnlyFemales(Filter):
    male_flag: Binary = SubjectValidator(data_type=Binary)

    def passes(self, composite: Dict) -> bool:
        male: bool = composites.get_property(composite, self.male_flag)
        return not male
