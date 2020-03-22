from typing import Dict, Any

from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.actions.step import Step
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema


class NestedFilter(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
    def __init__(self, content: NestableFilter):
        self.content: NestableFilter = content

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, context: "Context", schema: "Schema", content: Dict[str, Any], filters: bool = True, narrows: bool = True, pass_condition: str = "any") -> "NestedFilter":  # type: ignore
        assert isinstance(content, Dict), "NestedFilter content should be a dictionary"
        assert len(content) == 1, "NestedFilter content should contain the only direct child"

        filter_name, operand_specs = content.popitem()
        assert isinstance(operand_specs, list), "NestedFilter content should be a list"
        content_filter = LogicalOperator.build(context, schema, filter_name, filters=filters, narrows=narrows, pass_condition=pass_condition, operand_specs=operand_specs)
        return cls(content_filter)

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        self.content(origin_dir, target_dir)
