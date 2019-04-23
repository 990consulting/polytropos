from addict import Dict as Addict
from collections.abc import Callable
from collections import defaultdict
from etl4.ontology.track import Track
from etl4.ontology.variable import NamedList, List, Folder


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

    def translate_generic(self, variable_id, variable, document):
        # Try sources one by one
        for source in sorted(
            variable.sources,
            key=lambda source: self.source.variables[source].sort_order
        ):
            result = self.find_in_document(source, document)
            if result is not None:
                return result
        return None

    def translate_folder(self, variable_id, variable, document):
        return self(document, variable_id)

    def translate_list(self, variable_id, variable, document):
        pass

    def translate_named_list(self, variable_id, variable, document):
        pass

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
            translate = None
            if isinstance(variable, NamedList):
                translate = self.translate_named_list
            elif isinstance(variable, List):
                translate = self.translate_list
            elif isinstance(variable, Folder):
                translate = self.translate_folder
            else:
                translate = self.translate_generic

            output_document[variable.name] = translate(
                variable_id, variable, document
            )

        return output_document
