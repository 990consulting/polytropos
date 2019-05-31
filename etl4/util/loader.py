from os.path import basename, isfile, join
import glob
from importlib import import_module


def load(path, import_path, klass):
    # stackoverflow magic https://stackoverflow.com/a/1057765/225617
    modules = [
        basename(f)[:-3]
        for f in glob.glob(join(path, "*.py"))
        if isfile(f) and not f.endswith('__init__.py')
    ]

    for name in modules:
        import_module(import_path + '.' + name)

    return {
        cls.__name__: cls
        for cls in klass.__subclasses__()
    }
