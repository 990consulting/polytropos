from addict import Dict as Addict
from collections.abc import Callable
from collections import defaultdict
from etl4.ontology.track import Track


class Translate(Callable):
    def __init__(self, source: Track, target: Track):
        self.source = source
        self.target = target
        self.target_variables_by_parent = defaultdict(dict)
        for variable_id, variable in self.target.variables.items():
            self.target_variables_by_parent[
                variable.parent
            ][variable_id] = variable

    def find_in_document(self, variable_id, document):
        print(variable_id, document)
        if document is None:
            return None
        variable = self.source.variables[variable_id]
        if variable.parent:
            parent = self.find_in_document(
                variable.parent,
                document
            )
            if parent is None:
                return None
            return parent.get(variable.name)
        return document.get(variable.name)

    def __call__(self, document, parent=''):
        if isinstance(document, Addict):
            # Addict has a weird behavior when a key is not present and returns
            # a dict instead of None or throwing an exception
            document = document.to_dict()
        output_document = {}
        # Translate all variables with the same parent
        for variable_id, variable in self.target_variables_by_parent[
            parent
        ].items():
            # Start with None as a default value
            output_document[variable.name] = None
            # Then try sources one by one
            print(variable.sources)
            for source in sorted(
                variable.sources,
                key=lambda source: self.source.variables[source].sort_order
            ):
                output_document[variable.name] = self.find_in_document(
                    source, document
                )
                # Terminate the search if an actual value is found
                if output_document[variable.name] is not None:
                    break
            if output_document[variable.name] is None:
                container = self(document, variable_id)
                if container:
                    output_document[variable.name] = container
        return output_document
