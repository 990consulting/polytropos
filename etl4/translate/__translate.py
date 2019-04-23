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

    def find_in_document(self, variable_id, document, parent=''):
        if document is None:
            return None
        variable = self.source.variables[variable_id]
        if variable.parent != parent:
            parent = self.find_in_document(
                variable.parent,
                document
            )
            if parent is None:
                return None
            return parent.get(variable.name)
        return document.get(variable.name)

    def replace_sources(self, source_data):
        for variable_id, sources in source_data.items():
            self.target.variables[variable_id].sources = sources

    def translate_generic(self, variable_id, variable, document, parent):
        for source in sorted(
            variable.sources,
            key=lambda source: self.source.variables[source].sort_order
        ):
            result = self.find_in_document(source, document, parent)
            if result is not None:
                return result
        return None

    def translate_folder(self, variable_id, variable, document, parent):
        return self(document, variable_id, parent)

    def translate_list(self, variable_id, variable, document, parent):
        results = []
        for source in sorted(
            variable.sources,
            key=lambda source: self.source.variables[source].sort_order
        ):
            list_source = self.find_in_document(source, document, parent)
            self.replace_sources(variable.source_child_mappings[source])
            if list_source is None:
                continue
            for value in list_source:
                results.append(
                    self(
                        value,  # {self.source.variables[source].name: value},
                        variable_id,
                        source
                    )
                )
        return results

    def translate_named_list(self, variable_id, variable, document, parent):
        results = {}
        for source in sorted(
            variable.sources,
            key=lambda source: self.source.variables[source].sort_order
        ):
            list_source = self.find_in_document(source, document, parent)
            self.replace_sources(variable.source_child_mappings[source])
            if list_source is None:
                continue
            for key, value in list_source.items():
                if key in results:
                    # No duplicate keys
                    raise ValueError
                results[key] = self(
                    value,  # {self.source.variables[source].name: value},
                    variable_id,
                    source  # self.source.variables[source].name
                )
        return results

    def get_translate_function(self, variable):
        if isinstance(variable, NamedList):
            return self.translate_named_list
        elif isinstance(variable, List):
            return self.translate_list
        elif isinstance(variable, Folder):
            return self.translate_folder
        else:
            return self.translate_generic

    def __call__(self, document, parent='', source_parent=''):
        output_document = {}
        # Translate all variables with the same parent
        for variable_id, variable in self.target_variables_by_parent[
            parent
        ].items():
            translate = self.get_translate_function(variable)
            output_document[variable.name] = translate(
                variable_id, variable, document, source_parent
            )

        return output_document
