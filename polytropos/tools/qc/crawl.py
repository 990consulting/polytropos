from abc import abstractmethod
from typing import Dict, Optional, List as ListType, Any

from attr import dataclass

from polytropos.tools.qc import POLYTROPOS_NA, POLYTROPOS_CONFIRMED_NA
from polytropos.tools.qc.values import compare_primitives, CompareComplexVariable
from polytropos.util import nesteddicts

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable
from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch, MissingValue
import json

@dataclass
class Crawl:
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

    def _record_all_as_missing(self, f_subtree: Optional[Any], path: ListType[str]) -> None:
        """Recursively find all non-folders in the subtree, recording them as missing variables."""
        data_type: str
        if len(path) == 0:
            data_type = "Folder"
        else:
            var: Optional[Variable] = self.schema.lookup(path)
            assert var is not None
            data_type = var.data_type
        if data_type == "Folder":
            assert f_subtree is not None
            for key, subfolder in f_subtree.items():
                self._record_all_as_missing(subfolder, path + [key])
        else:
            var_path: str = nesteddicts.path_to_str(path)
            missing: MissingValue = MissingValue(self.entity_id, self.label, var_path, data_type, f_subtree)
            self.outcome.missings.append(missing)

    def _record_match(self, path: ListType, data_type: str, value: Optional[Any]) -> None:
        path_str = nesteddicts.path_to_str(path)
        match: ValueMatch = ValueMatch(self.entity_id, self.label, path_str, data_type, value)
        self.outcome.matches.append(match)

    def _record_missing(self, path: ListType, data_type: str, value: Optional[Any]) -> None:
        path_str = nesteddicts.path_to_str(path)
        missing: MissingValue = MissingValue(self.entity_id, self.label, path_str, data_type, value)
        self.outcome.missings.append(missing)

    def _record_mismatch(self, path: ListType, data_type: str, expected: Optional[Any], actual: Optional[Any]) -> None:
        path_str = nesteddicts.path_to_str(path)
        mismatch: ValueMismatch = ValueMismatch(self.entity_id, self.label, path_str, data_type, expected, actual)
        self.outcome.mismatches.append(mismatch)

    # TODO Since a_tree is now invariant, factor out the traverse/inspect logic into a class after tests pass
    def _handle_explicit_na(self, data_type: str, a_tree: Dict, path: ListType) -> None:
        a_val: Optional[Any] = nesteddicts.get(a_tree, path, default=POLYTROPOS_CONFIRMED_NA)
        if a_val == POLYTROPOS_NA:
            raise ValueError("Actual value contained ostensibly non-occurring sentinel value %s" % POLYTROPOS_NA)
        if a_val == POLYTROPOS_CONFIRMED_NA:
            self._record_match(path, data_type, POLYTROPOS_NA)
        else:
            self._record_mismatch(path, data_type, POLYTROPOS_NA, a_val)

    def _handle_explicit_none(self, data_type: str, a_tree: Dict, path: ListType) -> None:
        a_val: Optional[Any] = nesteddicts.get(a_tree, path, default=POLYTROPOS_CONFIRMED_NA)
        if a_val is None:
            self._record_match(path, data_type, None)
        else:
            self._record_mismatch(path, data_type, None, a_val)

    def _inspect_folder(self, f_tree: Dict, a_tree: Dict, path: ListType) -> None:
        assert f_tree != POLYTROPOS_NA  # Should have been handled at _inspect
        if f_tree is None:
            self._handle_explicit_none("Folder", a_tree, path)
            return

        for key, value in f_tree.items():
            self._inspect(key, value, a_tree, path)

    def _inspect_primitive(self, data_type: str, f_val: Optional[Any], a_tree: Dict, path: ListType) -> None:
        assert f_val != POLYTROPOS_NA  # Should have been handled at _inspect
        a_val: Optional[Any] = nesteddicts.get(a_tree, path, default=POLYTROPOS_CONFIRMED_NA)
        if a_val == POLYTROPOS_CONFIRMED_NA:
            self._record_missing(path, data_type, f_val)
        elif compare_primitives(f_val, a_val):
            self._record_match(path, data_type, f_val)
        else:
            self._record_mismatch(path, data_type, f_val, a_val)

    def _inspect_complex(self, data_type: str, f_val: Optional[Any], a_tree: Dict, path: ListType) -> None:
        assert f_val != POLYTROPOS_NA  # Should have been handled at _inspect
        a_val: Optional[Any] = nesteddicts.get(a_tree, path, default=POLYTROPOS_CONFIRMED_NA)
        if a_val == POLYTROPOS_CONFIRMED_NA:
            self._record_missing(path, data_type, json.dumps(f_val, sort_keys=True))
            return

        compare: CompareComplexVariable = CompareComplexVariable(self.schema)
        if compare(f_val, a_val, path=path):
            self._record_match(path, data_type, json.dumps(f_val, sort_keys=True))
        else:
            self._record_mismatch(path, data_type, json.dumps(f_val, sort_keys=True), json.dumps(a_val, sort_keys=True))

    def _inspect(self, key: str, f_tree: Optional[Any], a_tree: Dict, path: ListType[str]) -> None:
        child_path: ListType[str] = path + [key]
        var: Optional[Variable] = self.schema.lookup(child_path)
        if var is None:
            raise ValueError("No variable called %s (record %s). Value: %s" % (nesteddicts.path_to_str(path + [key]),
                                                                               self.entity_id, f_tree.__repr__()))
        data_type: str = var.data_type

        if f_tree == POLYTROPOS_NA:
            self._handle_explicit_na(data_type, a_tree, child_path)
            return

        if data_type == "Folder":
            assert isinstance(f_tree, dict)
            self._inspect_folder(f_tree, a_tree, child_path)
        elif data_type in {"List", "KeyedList"}:
            self._inspect_complex(data_type, f_tree, a_tree, child_path)
        else:
            self._inspect_primitive(data_type, f_tree, a_tree, child_path)

    def __call__(self) -> None:
        if self.actual is None:
            self._record_all_as_missing(self.fixture, [])
        else:
            self._inspect_folder(self.fixture, self.actual, [])

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
