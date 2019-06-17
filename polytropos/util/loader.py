def load(klass):
    return {
        cls.__name__: cls
        for cls in klass.__subclasses__()
    }
