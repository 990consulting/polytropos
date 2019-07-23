import logging
from collections.abc import Callable
from typing import Dict, List, Any, Optional

from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change
from polytropos.ontology.variable import Variable
from polytropos.util import nesteddicts

class _Crawl(Callable):
    def __init__(self, composite: Composite):
        self.composite = composite

    def _crawl_list(self, node: List, path: List, period: Optional[str]):
        for child in node:  # type: Dict
            self._crawl_folder(child, path, period)

    def _crawl_named_list(self, node: Dict, path: List, period: Optional[str]):
        for child in node.values():  # type: Dict
            self._crawl_folder(child, path, period)

    # noinspection PyUnresolvedReferences
    def _crawl_folder(self, node: Dict, path: List, period: Optional[str]):
        keys: List = list(node.keys())  # May need to delete a key, so create a copy
        for key in keys:
            if key.startswith("_"):
                logging.debug("Ignoring system variable %s" % nesteddicts.path_to_str(path + [key]))
                continue
            value = node[key]
            child_path = path + [key]

            var: Variable = self.composite.schema.lookup(child_path)
            if var is None:
                logging.warning("Unknown variable path %s in period %s of composite %s" %
                                (nesteddicts.path_to_str(path), period or "immutable", self.composite.composite_id))
                self._record_exception("unknown_vars", child_path, value, period)
                continue

            # Only primitives have the "cast" method
            try:
                casted: Any = var.cast(value)
                node[key] = casted
            except AttributeError:
                self._crawl(value, child_path, period)
            except ValueError:
                logging.warning('Could not cast value "%s" into data type "%s"' % (value, var.data_type))
                self._record_exception("cast_errors", path, {key: value}, period)
                del node[key]

    def _record_exception(self, exception_type: str, path: List[str], value: Optional[Any], period: Optional[str]):
        # Note: in the event that there is a list in the path, it will be omitted; hence, if there is more than one
        # exception in that list, you will only see a single example
        error_path: List[str] = [period or "immutable", "qc", "_exceptions", exception_type] + path
        nesteddicts.put(self.composite.content, error_path, value)

    def _crawl(self, node: Any, path: List, period: Optional[str]):
        if len(path) == 0:
            self._crawl_folder(node, path, period)
            return

        var: Variable = self.composite.schema.lookup(path)
        if var is None:
            logging.warning("Unknown variable path %s in composite %s" %
                            (nesteddicts.path_to_str(path), self.composite.composite_id))
            self._record_exception("unknown_vars", path, node, period)
            return

        if var.data_type == "List":
            self._crawl_list(node, path, period)

        elif var.data_type == "NamedList":
            self._crawl_named_list(node, path, period)

        elif var.data_type == "Folder":
            self._crawl_folder(node, path, period)

        else:
            raise ValueError

    def _cast_period(self, period: str):
        self._crawl(self.composite.content[period], [], period)

    def _cast_immutable(self):
        self._crawl(self.composite.content["immutable"], [], None)

    def __call__(self):
        for period in self.composite.periods:
            self._cast_period(period)
        if "immutable" in self.composite.content:
            self._cast_immutable()

class Cast(Change):
    """Crawls all periods (and immutable), casting variables according to their data type. Records an exception if a
    path exists that does not correspond to a variable. If a variable has a value that is incompatible with its variable
    type, it is deleted and Ignores paths that start with underscores."""

    def __call__(self, composite: Composite):
        crawl: _Crawl = _Crawl(composite)
        crawl()
