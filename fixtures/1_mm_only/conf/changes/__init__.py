from os.path import dirname, basename, isfile, join
import glob
from importlib import import_module
from etl4.ontology.metamorphosis.__change import Change

# TODO Quimey, please include a link to the SO thread where you found it
# stackoverflow magic
modules = [
    basename(f)[:-3]
    for f in glob.glob(join(dirname(__file__), "*.py"))
    if isfile(f) and not f.endswith('__init__.py')
]

for name in modules:
    module = import_module('fixtures.conf.changes.' + name)

all_changes = {
    cls.__name__: cls
    for cls in Change.__subclasses__()
}
