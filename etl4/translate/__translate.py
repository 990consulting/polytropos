from collections.abc import Callable
from etl4.ontology.track import Track

class Translate(Callable):
    def __init__(self, source: Track, target: Track):
        pass

    def __call__(self, *args, **kwargs):
        pass
