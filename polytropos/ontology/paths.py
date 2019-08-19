from dataclasses import dataclass
import os


@dataclass
class PathLocator:
    """Path locator class. It knows the internal structure of a Polytropos environment."""
    conf: str
    data: str

    @property
    def conf_dir(self) -> str:
        return self.conf

    @property
    def data_dir(self) -> str:
        return self.data

    @property
    def tasks_dir(self) -> str:
        return os.path.join(self.conf_dir, 'tasks')

    @property
    def schemas_dir(self) -> str:
        return os.path.join(self.conf_dir, 'schemas')

    @property
    def lookups_dir(self) -> str:
        return os.path.join(self.data_dir, 'lookups')

    @property
    def entities_dir(self) -> str:
        return os.path.join(self.data_dir, 'entities')
