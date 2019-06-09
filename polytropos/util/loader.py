import os
import sys
import importlib
import glob


def load(path, conf, klass):
    # stackoverflow magic https://stackoverflow.com/a/1057765/225617
    path = os.path.relpath(path)
    modules = [
        os.path.basename(f)[:-3]
        for f in glob.glob(os.path.join(path, "*.py"))
        if os.path.isfile(f) and not f.endswith('__init__.py')
    ]
    base = os.path.dirname(os.path.dirname(conf))
    sys.path.append(base)
    name = os.path.relpath(path, base).replace('/', '.')
    for module in modules:
        importlib.import_module(name + '.' + module)

    return {
        cls.__name__: cls
        for cls in klass.__subclasses__()
    }
