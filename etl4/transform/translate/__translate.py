import logging
from collections.abc import Callable
from collections import defaultdict
from etl4.ontology.track import Track
from etl4.ontology.variable import NamedList, List, Folder
from etl4.transform.translate.__reporter import Reporter


class Translate(Callable):
    """Class in charge of translating documents given a source track and a
    target track"""
    def __init__(self, target: Track):
        self.source = target.source
        self.target = target
        # We need to group by variables by parent to be able to efficiently do
        # a recursion in the translate function
        self.target_variables_by_parent = defaultdict(dict)
        self.reporter = Reporter()
        for variable_id, variable in self.target.variables.items():
            self.target_variables_by_parent[
                variable.parent
            ][variable_id] = variable

    def find_in_document(self, variable_id, document, parent=''):
        """Function that finds a variable (given its id) in a document. The
        parent parameter is used to limit the depth for the recursive search"""
        if document is None:
            return None
        variable = self.source.variables[variable_id]
        if variable.parent != parent:
            # recursively find the parent in the document
            parent = self.find_in_document(
                variable.parent,
                document,
                parent
            )
            if parent is None:
                return None
            # now our variable is a direct child of the parent
            return parent.get(variable.name)
        # we are at root level so we return the value extracted directly from
        # the document
        return document.get(variable.name)

    def replace_sources(self, source_data):
        """This function replaces sources of target variables using a dict of
        variable_id -> new sources. This is used to move the
        source_child_mappings from the parent to the childs"""
        for variable_id, sources in source_data.items():
            # skip validation
            self.target.variables[variable_id].__dict__['sources'] = sources

    def translate_generic(self, variable_id, variable, document, parent):
        """Translate for primitive (non-container) variables"""
        # Just look for the value in the sources, sorted using `sort_order`
        for source in sorted(
            variable.sources,
            key=lambda source: self.source.variables[source].sort_order
        ):
            result = self.find_in_document(source, document, parent)
            if result is not None:
                return result
        return None

    def translate_folder(self, variable_id, variable, document, parent):
        """Translate for folders"""
        # Just translate all variables in the folder
        return self(document, variable_id, parent)

    def translate_list(self, variable_id, variable, document, parent):
        """Translate for lists"""
        results = []
        # The resulting list is the concatenation of all the translations,
        # source by source
        for source in variable.sources:
            # get the document values for the current source
            list_source = self.find_in_document(source, document, parent)
            # update the sources for the source variables
            self.replace_sources(variable.source_child_mappings[source])
            if list_source is None:
                continue
            for value in list_source:
                # translate the values in the list one by one and add them to
                # the result
                results.append(
                    self(
                        value,
                        variable_id,
                        source
                    )
                )
        return results

    def translate_named_list(self, variable_id, variable, document, parent):
        """Translate function for named lists (similar to python dicts), the
        logic is almost the same as for lists but taking care of the keys.
        Raises ValueError on duplicate keys"""
        results = {}
        for source in variable.sources:
            list_source = self.find_in_document(source, document, parent)
            self.replace_sources(variable.source_child_mappings[source])
            if list_source is None:
                continue
            for key, value in list_source.items():
                if key in results:
                    # No duplicate keys
                    raise ValueError
                results[key] = self(
                    value,
                    variable_id,
                    source
                )
        return results

    def get_translate_function(self, variable):
        """Python polymorfism"""
        if isinstance(variable, NamedList):
            return self.translate_named_list
        elif isinstance(variable, List):
            return self.translate_list
        elif isinstance(variable, Folder):
            return self.translate_folder
        else:
            return self.translate_generic

    def set_document_name(self, name):
        self.reporter.set_document_name(name)

    def __call__(self, document, parent='', source_parent=''):
        output_document = {}
        # Translate all variables with the same parent
        for variable_id, variable in self.target_variables_by_parent[
            parent
        ].items():
            try:
                translate = self.get_translate_function(variable)
                output_document[variable.name] = translate(
                    variable_id, variable, document, source_parent
                )
                self.reporter.report(
                    variable_id, variable, output_document[variable.name]
                )
            except:
                logging.warning('Error translating variable %s', variable_id)
                output_document[variable.name] = None
        return output_document
