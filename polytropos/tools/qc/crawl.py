from abc import abstractmethod
from typing import Callable, Dict, Optional, List as ListType, Any

from attr import dataclass

from polytropos.tools.qc.values import compare_primitives, CompareComplexVariable
from polytropos.util.nesteddicts import str_to_path, path_to_str

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable
from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch, MissingValue

@dataclass
class Crawl(Callable):
    """Crawl a data tree (either a temporal period or the immutable fact set) of the fixture, detecting noting successes
    and failures."""

    entity_id: str
    schema: Schema
    fixture: Dict
    actual: Optional[Dict]

    outcome: Outcome

    @property
    @abstractmethod
    def temporal(self) -> bool:
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        pass

    def _crawl_folder(self, f_subtree: Dict, a_subtree: Optional[Any], path: ListType):
        # If the actual variable is not a folder, the whole subtree is a mismatch
        if not isinstance(a_subtree, dict):
            var_path: str = path_to_str(path)
            mismatch: ValueMismatch = ValueMismatch(self.entity_id, self.label, var_path, "Folder", f_subtree,
                                                    a_subtree)
            self.outcome.mismatches.append(mismatch)
            return

        for key in f_subtree.keys():
            self._inspect(key, f_subtree, a_subtree, path)

    def _inspect_primitive(self, data_type: str, f_val: Optional[Any], a_val: Optional[Any], path: ListType):
        # NOTE: Since we reached this point by crawling the fixture (in __call__), if f_subtree is null, it means the
        # fixture explicitly called it null (rather than simply having omitted it)
        var_path: str = path_to_str(path)
        if compare_primitives(f_val, a_val):
            match: ValueMatch = ValueMatch(self.entity_id, self.label, var_path, data_type, f_val)
            self.outcome.matches.append(match)
        else:
            mismatch: ValueMismatch = ValueMismatch(self.entity_id, self.label, var_path, data_type, f_val, a_val)
            self.outcome.mismatches.append(mismatch)

    def _traverse(self, data_type: str, f_subtree: Dict, a_subtree: Optional[Dict], path: ListType):
        if data_type in {"List", "NamedList"}:
            self._inspect_complex(data_type, f_subtree, a_subtree, path)
        elif data_type == "Folder":
            self._crawl_folder(f_subtree, a_subtree, path)
        else:
            self._inspect_primitive(data_type, f_subtree, a_subtree, path)

    def _inspect_complex(self, data_type: str, f_subtree: Optional[Any], a_subtree: Optional[Any], path: ListType):
        var_path: str = path_to_str(path)
        compare: CompareComplexVariable = CompareComplexVariable(self.schema)
        if compare(f_subtree, a_subtree, path=path):
            match: ValueMatch = ValueMatch(self.entity_id, self.label, var_path, data_type, f_subtree)
            self.outcome.matches.append(match)
        else:
            mismatch: ValueMismatch = ValueMismatch(self.entity_id, self.label, var_path, data_type, f_subtree,
                                                    a_subtree)
            self.outcome.mismatches.append(mismatch)

    def _record_all_as_missing(self, f_subtree: Optional[Any], path: ListType[str]):
        """Recursively find all non-folders in the subtree, recording them as missing variables."""
        if len(path) == 0:
            data_type: str = "Folder"
        else:
            var: Variable = self.schema.lookup(path)
            data_type: str = var.data_type
        if data_type == "Folder":
            for key, subfolder in f_subtree.items():
                self._record_all_as_missing(subfolder, path + [key])
        else:
            var_path: str = path_to_str(path)
            missing: MissingValue = MissingValue(self.entity_id, self.label, var_path, data_type, f_subtree)
            self.outcome.missings.append(missing)

    def _inspect(self, key: str, f_tree: Dict, a_tree: Dict, path: ListType):
        var: Variable = self.schema.lookup(path + [key])
        if var is None:
            raise ValueError("No variable called %s" % path_to_str(path))
        data_type: str = var.data_type
        f_subtree: Optional[Any] = f_tree[key]
        if key not in a_tree:
            self._record_all_as_missing(f_subtree, path + [key])
        else:
            a_subtree: Optional[Any] = a_tree[key]  # Null means explicit null
            self._traverse(data_type, f_subtree, a_subtree, path + [key])

    def __call__(self):
        if self.actual is None:
            self._record_all_as_missing(self.fixture, [])
        else:
            for key in self.fixture.keys():  # type: str
                self._inspect(key, self.fixture, self.actual, [])

@dataclass
class CrawlPeriod(Crawl):
    period: str

    @property
    def temporal(self) -> bool:
        return True

    @property
    def label(self) -> str:
        return self.period

class CrawlImmutable(Crawl):

    @property
    def temporal(self) -> bool:
        return False

    @property
    def label(self) -> str:
        return "immutable"