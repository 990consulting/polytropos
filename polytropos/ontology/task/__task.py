import logging
import os
import shutil
from typing import Optional, Any, List, Dict

import yaml
from tempfile import mkdtemp
from polytropos.actions.consume import Consume
from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.ontology.context import Context

# Import all action types so that they can be registered as subclasses
from polytropos.actions.evolve.__evolve import Evolve
from polytropos.actions.scan import Scan
from polytropos.actions.filter import Filter
from polytropos.actions.aggregate import Aggregate
from polytropos.actions.translate import Translate
from polytropos.actions.filter.sequential_filter import SequentialFilter  # This is a subclass of Step, not of Filter
from polytropos.actions.filter.nested_filter import NestedFilter  # This is a subclass of Step, not of Filter

# Step class name deserialization
STEP_TYPES = {
    cls.__name__: cls
    for cls in Step.__subclasses__()
}

class Task:
    def __init__(
        self, context: Context,
        origin_data: Any, origin_schema: Schema,
        target_data: Optional[Any] = None, target_schema: Optional[Schema] = None
    ):
        self.context = context
        self.origin_data = origin_data
        self.origin_schema = origin_schema
        self.target_data = target_data
        self.target_schema = target_schema
        self.steps: List[Step] = []

    @classmethod
    def build(cls, context: Context, name: str) -> "Task":
        """Build task from yaml, read all input data and create corresponding
        objects"""
        logging.info("Constructing task execution plan.")
        logging.info("Configuration base directory is %s; entities directory is %s." % (context.conf_dir, context.entities_input_dir))
        task_path: str = os.path.join(context.conf_dir, 'tasks', name + '.yaml')
        with open(task_path, 'r') as f:
            logging.info("Task configuration loaded from %s." % task_path)
            spec = yaml.safe_load(f)
        resulting_in = spec.get('resulting_in', {})
        origin_schema = Schema.load(spec['starting_with']['schema'], context.schemas_dir)
        assert origin_schema is not None
        task = cls(
            context=context,
            origin_data=spec['starting_with']['data'],
            origin_schema=origin_schema,
            target_data=resulting_in.get('data'),
            target_schema=Schema.load(resulting_in.get('schema'), context.schemas_dir)
        )
        task.load_steps(spec['steps'])
        # If the last step is a Consume step we don't need target data
        assert task.target_data is not None or isinstance(task.steps[-1], Consume)
        return task

    def load_steps(self, step_descriptions: List[Dict[str, Any]]) -> None:
        """Load steps of the current task"""
        logging.info("Initializing task pipeline steps.")
        current_schema = self.origin_schema
        for step in step_descriptions:
            # expect only one key/value pair
            assert len(step) == 1, (
                'Step description can have only one key, value pair'
            )
            for class_name, args in step.items():
                if class_name == "Filter" and LogicalOperator.is_logical_operator(args["name"]):
                    raise ValueError("LogicalOperator filter can be used in NestedFilter only")

                # Sequential filters have a list of arguments
                if class_name == "SequentialFilter":
                    step_instance: Step = SequentialFilter.build(self.context, current_schema, *args)  # type: ignore
                # Everything else takes a dict of arguments
                else:
                    step_instance: Step = self.append_normal_step(class_name, current_schema, args)  # type: ignore

                self.steps.append(step_instance)

                # Aggregation changes schema
                if class_name in ('Aggregate', 'Translate'):
                    assert isinstance(step_instance, Aggregate) or isinstance(step_instance, Translate)
                    # noinspection PyUnresolvedReferences
                    current_schema = step_instance.target_schema

    def append_normal_step(self, class_name: str, current_schema: Schema, kwargs: Dict) -> Step:
        step_type = STEP_TYPES[class_name]
        try:
            step_instance: Step = step_type.build(
                context=self.context, schema=current_schema, **kwargs
            )
        except Exception as e:
            print("breakpoint")
            raise e
        return step_instance

    def run(self) -> None:
        """Run the task: run steps one by one handling intermediate outputs in
        temporary folders"""
        origin_path = os.path.join(self.context.entities_input_dir, self.origin_data) if self.context.legacy_mode else self.context.entities_input_dir
        logging.info("Running task with origin data in %s." % origin_path)
        task_output_path: Optional[str] = None
        if self.target_data is not None:
            task_output_path = os.path.join(
                self.context.entities_output_dir, self.target_data
            ) if self.context.legacy_mode else self.context.entities_output_dir
        # There are always two paths in play, current and next, each step
        # will read from current and write to next, after the step is done we
        # can delete the current_path folder because it's not used anymore
        current_path: str = origin_path
        next_path: Optional[str] = None
        for i, step in enumerate(self.steps):
            logging.info("Beginning a %s step (%d)." % (step.__class__.__name__, i))

            is_last_step = i == len(self.steps) - 1
            if is_last_step and task_output_path is not None:
                next_path = task_output_path
            else:
                next_path = mkdtemp(dir=self.context.temp_dir, prefix=str(i).zfill(3) + '-')

            logging.debug("Output for this step will be recorded in %s." % next_path)
            step(current_path, next_path)

            if i > 0 and not self.context.no_cleanup:
                shutil.rmtree(current_path, ignore_errors=True)
            current_path = next_path

        assert next_path is not None
        if task_output_path is None and not self.context.no_cleanup:
            shutil.rmtree(next_path, ignore_errors=True)
