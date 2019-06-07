from dataclasses import dataclass
from typing import Dict

from etl4.ontology.filter import Filter
from etl4.ontology.metamorphosis.__subject import SubjectValidator
from etl4.ontology.variable.__variable import Binary
from etl4.util import composites

@dataclass
class RetainOnlyFemales(Filter):
    male_flag: Binary = SubjectValidator(data_type=Binary)

    def passes(self, composite: Dict) -> bool:
        male: bool = composites.get_property(composite, self.male_flag)
        return not male
