import csv
import json
import os
import logging
from typing import Type, Callable, Any, Dict, List, Optional, Sequence, cast
from collections import OrderedDict

def lookup(name: str) -> Callable[[Type], Type]:
    """Intended to be a decorator on the constructor for a Change. Verifies that the specified lookup table has been
    loaded."""
    def decorator(cls: Type) -> Type:
        old_init = cls.__init__

        def __init__(self: Any, *args: Any, **kwargs: Any) -> None:
            old_init(self, *args, **kwargs)
            if name not in kwargs['lookups']:
                raise ValueError(f'Lookup {name} not loaded')

        cls.__init__ = __init__
        return cls
    return decorator

def _resolve_filename(lookup_name: str, base_dir: str) -> str:
    no_extension: str = os.path.join(base_dir, lookup_name)
    csv_filename: str = no_extension + ".csv"
    json_filename: str = no_extension + ".json"
    if os.path.exists(csv_filename) and os.path.exists(json_filename):
        raise ValueError('Found both .csv and .json files for lookup "{}"'.format(lookup_name))
    elif os.path.exists(csv_filename):
        return csv_filename
    elif os.path.exists(json_filename):
        return json_filename
    else:
        raise FileNotFoundError('Unable to locate .csv or .json lookup for "{}" in basepath "{}"'
                                .format(lookup_name, base_dir))

def _load_csv(filename: str, lookup_name: str) -> Dict:
    ret: Dict[str, Dict] = OrderedDict()
    with open(filename) as fh:
        reader: csv.DictReader = csv.DictReader(fh)
        fieldnames: Sequence[str] = cast(Sequence[str], reader.fieldnames)
        key_column: str = fieldnames[0]
        logging.info('Treating first column ({}) as key column for .csv lookup "{}"'.format(key_column, lookup_name))
        for row in reader:
            key: str = row[key_column]
            if key in ret:
                raise ValueError('Duplicate key "{}" in lookup "{}"'.format(key, lookup_name))
            content: Dict = row.copy()
            del content[key_column]
            ret[key] = content
    return ret

def _load_json(filename: str) -> Dict:
    with open(filename) as fh:
        return json.load(fh)

def _load(filename: str, lookup_name: str) -> Dict:
    if filename.endswith(".csv"):
        return _load_csv(filename, lookup_name)
    elif filename.endswith(".json"):
        return _load_json(filename)
    else:
        raise RuntimeError('Unexpected lookup filename {} for lookup "{}"'.format(filename, lookup_name))

def load_lookups(requested: Optional[List[str]], base_dir: str) -> Dict:
    """Look for a set of lookups (.json or .csv) in a particular directory. Load them into a dictionary of
    dictionaries, then return that. Verify that there is not both a .json and a .csv file with the same name in the
    same directory."""
    if requested is None or len(requested) == 0:
        return {}
    loaded_lookups: Dict = {}
    for lookup_name in requested:
        filename: str = _resolve_filename(lookup_name, base_dir)
        content: Dict = _load(filename, lookup_name)
        loaded_lookups[lookup_name] = content
    return loaded_lookups
