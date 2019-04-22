from addict import Dict as Addict
from collections.abc import Callable
from etl4.ontology.track import Track

class Translate(Callable):
    def __init__(self, source: Track, target: Track):
        self.source = source
        self.target = target

    def __call__(self, document):
        if isinstance(document, Addict):
            # Addict has a weird behavior when a key is not present and returns
            # a dict instead of None or throwing an exception
            document = document.to_dict()
        output_document = {}
        # Translate all variables
        for variable_id, variable in self.target.variables.items():
            # Start with None as a default value
            output_document[variable.name] = None
            # Then try sources one by one
            for source in variable.sources:
                if source in self.source.variables:
                    output_document[variable.name] = document.get(
                        self.source.variables[source].name
                    )
                    # Terminate the search if an actual value is found
                    if output_document[variable.name] is not None:
                        break
        return output_document
