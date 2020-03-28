from typing import Dict, Any, cast

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

        filter_class_name, filter_spec = content.popitem()
        if LogicalOperator.is_logical_operator(filter_class_name):
            assert isinstance(filter_spec, list), "LogicalOperator content should be a list"
            content_filter = LogicalOperator.build(context, schema, filter_class_name, filters=filters, narrows=narrows, pass_condition=pass_condition, operand_specs=filter_spec)
        else:
            content_filter = NestableFilter.build(context, schema, filter_class_name, filters=filters, narrows=narrows, pass_condition=pass_condition, **filter_spec)
        return cls(cast(NestableFilter, content_filter))

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        self.content(origin_dir, target_dir)
