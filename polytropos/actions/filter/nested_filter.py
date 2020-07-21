from typing import Dict, Any, cast

from polytropos.ontology.composite import Composite

from polytropos.actions.filter import Filter
from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.actions.step import Step
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

class NestedFilter(Filter):  # type: ignore # https://github.com/python/mypy/issues/5374

    def __init__(self, context: Context, schema: Schema, content: Dict, filters: bool = True, narrows: bool = True,
                 pass_condition: str = "any"):
        super().__init__(context, schema)
        assert isinstance(content, Dict), "NestedFilter content should be a dictionary"
        assert len(content) == 1, "NestedFilter content should contain the only direct child"

        filter_class_name, filter_spec = content.popitem()

        self.child: NestableFilter
        if LogicalOperator.is_logical_operator(filter_class_name):
            assert isinstance(filter_spec, list), "LogicalOperator content should be a list"
            self.child = cast(NestableFilter, LogicalOperator.build(context, schema, filter_class_name, filters=filters,
                                                                    narrows=narrows, pass_condition=pass_condition,
                                                                    operand_specs=filter_spec))
        else:
            self.child = cast(NestableFilter, NestableFilter.build(context, schema, filter_class_name, filters=filters,
                                                                   narrows=narrows, pass_condition=pass_condition,
                                                                   **filter_spec))

    def passes(self, composite: Composite) -> bool:
        """Evaluate whether the entire Composite should be included at the next Step or not."""
        return self.child.passes(composite)

    def narrow(self, composite: Composite) -> None:
        """Remove or retain specific periods."""
        self.child.narrow(composite)
