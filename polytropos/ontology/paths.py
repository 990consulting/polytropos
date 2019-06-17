from dataclasses import dataclass
import os


@dataclass
class PathLocator:
    """Path locator class. It knows the internal structure of a Polytropos environment."""
    conf: str
    data: str

    @property
    def conf_dir(self):
        return self.conf

    @property
    def data_dir(self):
        return self.data

    @property
    def tasks_dir(self):
        return os.path.join(self.conf_dir, 'tasks')

    @property
    def changes_dir(self):
        return os.path.join(self.conf_dir, 'changes')

    @property
    def changes_import(self):
        return os.path.relpath(
            self.changes_dir, self.base_dir
        ).replace('/', '.')

    @property
    def scans_dir(self):
        return os.path.join(self.conf_dir, 'scans')

    @property
    def scans_import(self):
        return os.path.relpath(
            self.scans_dir, self.base_dir
        ).replace('/', '.')

    @property
    def aggregations_dir(self):
        return os.path.join(self.conf_dir, 'aggregations')

    @property
    def aggregations_import(self):
        return os.path.relpath(
            self.aggregations_dir, self.base_dir
        ).replace('/', '.')

    @property
    def filters_dir(self):
        return os.path.join(self.conf_dir, 'filters')

    @property
    def filters_import(self):
        return os.path.relpath(
            self.filters_dir, self.base_dir
        ).replace('/', '.')

    @property
    def consumes_dir(self):
        return os.path.join(self.conf_dir, 'consumers')

    @property
    def consumes_import(self):
        return os.path.relpath(
            self.consumes_dir, self.base_dir
        ).replace('/', '.')

    @property
    def schemas_dir(self):
        return os.path.join(self.conf_dir, 'schemas')

    @property
    def lookups_dir(self):
        return os.path.join(self.data_dir, 'lookups')

    @property
    def entities_dir(self):
        return os.path.join(self.data_dir, 'entities')
