import logging
import os
from shutil import rmtree
from typing import Type

import yaml
from tempfile import TemporaryDirectory
from polytropos.actions.consume import Consume
from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.ontology.paths import PathLocator

# Import all action types so that they can be registered as subclasses
from polytropos.actions.evolve.__evolve import Evolve
from polytropos.actions.scan import Scan
from polytropos.actions.filter import Filter
from polytropos.actions.aggregate import Aggregate
from polytropos.actions.translate import Translate

# Step class name deserialization
STEP_TYPES = {
    cls.__name__: cls
    for cls in Step.__subclasses__()
}

class Task:
    def __init__(
        self, path_locator,
        origin_data, origin_schema,
        target_data=None, target_schema=None
    ):
        self.path_locator = path_locator
        self.origin_data = origin_data
        self.origin_schema = origin_schema
        self.target_data = target_data
        self.target_schema = target_schema
        self.steps = []

    @classmethod
    def build(cls, conf_dir, data_dir, name):
        """Build task from yaml, read all input data and create corresponding
        objects"""
        logging.info("Constructing task execution plan.")
        path_locator = PathLocator(conf=conf_dir, data=data_dir)
        logging.info("Configuration base directory is %s; data base directory is %s." % (conf_dir, data_dir))
        task_path: str = os.path.join(path_locator.tasks_dir, name + '.yaml')
        with open(task_path, 'r') as f:
            logging.info("Task configuration loaded from %s." % task_path)
            spec = yaml.safe_load(f)
        resulting_in = spec.get('resulting_in', {})
        task = cls(
            path_locator=path_locator,
            origin_data=spec['starting_with']['data'],
            origin_schema=Schema.load(spec['starting_with']['schema'], path_locator=path_locator),
            target_data=resulting_in.get('data'),
            target_schema=Schema.load(resulting_in.get('schema'), path_locator=path_locator)
        )
        task.load_steps(spec['steps'])
        # If the last step is a Consume step we don't need target data
        assert task.target_data is not None or isinstance(task.steps[-1], Consume)
        return task

    def load_steps(self, step_descriptions):
        """Load steps of the current task"""
        logging.info("Initializing task pipeline steps.")
        current_schema = self.origin_schema
        for step in step_descriptions:
            # expect only one key/value pair
            assert len(step) == 1, (
                'Step description can have only one key, value pair'
            )
            for class_name, kwargs in step.items():
                step_type: Type = STEP_TYPES[class_name]
                try:
                    step_instance: Step = step_type.build(
                        path_locator=self.path_locator, schema=current_schema, **kwargs
                    )
                except Exception as e:
                    print("breakpoint")
                    raise e
                self.steps.append(step_instance)

                # Aggregation changes schema
                if class_name in ('Aggregate', 'Translate'):
                    # noinspection PyUnresolvedReferences
                    current_schema = step_instance.target_schema

    def run(self):
        """Run the task: run steps one by one handling intermediate outputs in
        temporary folders"""
        origin_path = os.path.join(self.path_locator.entities_dir, self.origin_data)
        logging.info("Running task with origin data in %s." % origin_path)
        if self.target_data is not None:
            task_output_path = os.path.join(
                self.path_locator.entities_dir, self.target_data
            )
            try:
                logging.debug("Attempting to remove old task output directory, if it exists.")
                rmtree(task_output_path)
                logging.debug("Old output directory removed.")
            except FileNotFoundError:
                logging.debug("No old task output directory.")
                pass
            logging.debug("Creating task output directory.")
            os.mkdir(task_output_path)
        # There are always two paths in play, current and next, each step
        # will read from current and write to next, after the step is done we
        # can delete the current_path folder because it's not used anymore
        current_path = origin_path
        current_path_obj = None
        next_path = None
        for step in self.steps:
            logging.info("Beginning a %s step." % step.__class__.__name__)
            next_path = TemporaryDirectory(dir=self.path_locator.data_dir)
            logging.debug("Output for this step will be recorded in %s." % next_path)
            step(current_path, next_path.name)
            if current_path_obj:
                current_path_obj.cleanup()
            current_path = next_path.name
            current_path_obj = next_path
        if self.target_data is not None:
            # Move the last temporary folder to destination
            logging.info("Renaming %s to %s" % (next_path.name, task_output_path))
            os.rename(next_path.name, task_output_path)
            # Hack to avoid leaving unfinished objects
            os.mkdir(next_path.name)
        next_path.cleanup()
