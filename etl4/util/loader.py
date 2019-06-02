from os.path import basename, isfile, join
import glob
import importlib


def load(path, klass):
    # stackoverflow magic https://stackoverflow.com/a/1057765/225617
    modules = [
        (basename(f)[:-3], f)
        for f in glob.glob(join(path, "*.py"))
        if isfile(f) and not f.endswith('__init__.py')
    ]

    base = klass.__name__.lower()
    for name, path in modules:
        spec = importlib.util.spec_from_file_location(base + '.' + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    return {
        cls.__name__: cls
        for cls in klass.__subclasses__()
    }
