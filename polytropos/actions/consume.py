import os
import json
import csv
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.util.loader import load
from polytropos.util.composites import get_property, get_observation
from polytropos.ontology.task.__paths import TaskPathLocator


# TODO Quimey, unlike the other tasks, consumers may take arguments that are not variables. We may want the ability to
#  do this in general--for example, if a task does a statistical analysis and we want to provide some tuning parameter.
#  I'm not sure if this actually creates a problem or not.
@dataclass
class Consume(Step):
    path_locator: TaskPathLocator
    schema: Schema

    """Export data from a set of composites to a single file."""
    @classmethod
    def build(cls, path_locator, schema, name, **kwargs):
        consumes = load(cls)
        return consumes[name](path_locator, schema, **kwargs)

    def before(self):
        """Optional actions to be performed after the constructor runs but before starting to consume composites."""
        pass

    def after(self):
        """Optional actions to be performed after the composites are all consumed."""

    @abstractmethod
    def consume(self, composite_id: str, composite: Dict):
        pass

    def __call__(self, origin, target):
        """Generate the export file."""
        self.before()
        for filename in sorted(os.listdir(origin)):
            with open(os.path.join(origin, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                self.consume(filename[:-5], composite)
        self.after()


@dataclass
class ExportToJSON(Consume):
    filename: str
    indent: int = 2

    def __post_init__(self):
        self.fobj = None
        self.first = True

    def before(self):
        self.fobj = open(
            os.path.join(self.path_locator.conf, '../', self.filename), 'w'
        )
        self.fobj.write('{\n')

    def consume(self, composite_id, composite):
        if not self.first:
            self.fobj.write(',\n')
        self.first = False
        self.fobj.write(' ' * self.indent + f'"{composite_id}": ')
        data = json.dumps(composite, indent=self.indent).split('\n')
        for i, line in enumerate(data):
            if i:
                self.fobj.write('\n')
                self.fobj.write(' ' * self.indent)
            self.fobj.write(line)

    def after(self):
        self.fobj.write('\n}')
        self.fobj.close()


@dataclass
class ExportToCSV(Consume):
    filename: str
    columns: Dict
    immutable: bool

    def __post_init__(self):
        self.fobj = None
        self.fields = ['composite_id']
        self.column_vars = {}
        print(self.columns)
        if not self.immutable:
            self.fields.append('period')
        for column in self.columns:
            self.__process_columns(column)
        for name, var in self.column_vars.items():
            print(name, var)


    def __process_columns(self, column):
        if isinstance(column, dict):
            for key, attributes in column.items():
                self.column_vars[key] = self.schema.get(key)
                self.fields.append(key)
                for name, value in attributes.items():
                    if name == 'children':
                        for child in value:
                            self.__process_columns(child)
                    elif name == 'alias':
                        pass
                    else:
                        raise NotImplementedError
        elif isinstance(column, str):
            self.column_vars[column] = self.schema.get(column)
            self.fields.append(column)
        else:
            raise AttributeError

    def get_rows(self, composite_id, composite):
        if self.immutable:
            data = {
                name: get_property(composite, var)
                for name, var in self.column_vars.items()
            }
            data['composite_id'] = composite_id
            yield [data]
        else:
            for period, value in composite.items():
                if period.isdigit():
                    row = {}
                    row['composite_id'] = composite_id
                    row['period'] = period
                    for name, var in self.column_vars.items():
                        row[name] = get_observation(
                            composite, period, var, True
                        )
                    yield row

    def before(self):
        self.fobj = open(
            os.path.join(self.path_locator.conf, '../', self.filename), 'w'
        )
        self.writer = csv.DictWriter(self.fobj, self.fields)
        self.writer.writeheader()

    def consume(self, composite_id, composite):
        for row in self.get_rows(composite_id, composite):
            self.writer.writerow(row)

    def after(self):
        self.fobj.close()
