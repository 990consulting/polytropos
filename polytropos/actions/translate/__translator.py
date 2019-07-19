import logging
from collections.abc import Callable
from collections import defaultdict
from polytropos.ontology.track import Track
from polytropos.ontology.variable import NamedList, List, Folder, Variable
from typing import TYPE_CHECKING, Dict, Optional, Any

#if TYPE_CHECKING:
#    from polytropos.ontology.variable import Variable

class SourceNotFoundException(RuntimeError):
    pass

class Translator(Callable):
    """Class in charge of translating documents given a source track and a
    target track"""
    def __init__(self, target: Track, failsafe: bool=False):
        logging.info('Initializing translator for track "%s".' % target.name)
        if failsafe:
            logging.warning("Translation errors will be ignored! Use at your own risk!")
        self.source: Track = target.source
        self.target: Track = target

        # We need to group by variables by parent to be able to efficiently do
        # a recursion in the translate function
        # NB: `defaultdict(dict)` means "Create a dictionary that automatically supplies missing values"--very nice
        self.target_variables_by_parent: Dict = defaultdict(dict)
        logging.debug("Grouping variables by parents.")
        for variable_id, variable in self.target.items():  # type: str, "Variable"
            self.target_variables_by_parent[variable.parent][variable_id] = variable
        # when failsafe is true exceptions are caught and ignored
        self.failsafe = failsafe

    def find_in_document(self, variable_id: str, document: Dict, parent='') -> Optional[Any]:
        """Function that finds a variable (given its id) in a document. The
        parent parameter is used to limit the depth for the recursive search"""
        assert document is not None, "Unexpected situation occurred -- study"
        # TODO What type is parent supposed to be here? Play around to find out.
        if len(document) == 0:
            raise SourceNotFoundException
        variable = self.source[variable_id]
        if variable.parent != parent:
            # recursively find the parent in the document
            parent_doc = self.find_in_document(
                variable.parent,
                document,
                parent
            )
            if parent_doc is None or variable.name not in parent_doc:
                raise SourceNotFoundException
            # now our variable is a direct child of the parent and we know it's present
            return parent_doc[variable.name]
        # we are at root level so we return the value extracted directly from
        # the document
        if variable.name not in document:
            raise SourceNotFoundException
        return document[variable.name]

    def translate_generic(self, variable_id: str, variable, document, parent):
        """Translate for primitive (non-container) variables"""
        # We have to restrict the sources to the descendants of parent
        parent_source = None
        if parent:
            parent_source = variable.track.source[parent]
        for source in variable.sources:
            if parent_source and not parent_source.check_ancestor(source):
                continue
            try:
                result = self.find_in_document(source, document, parent)
            # If we get a SourceNotFoundError, the source variable simply did not exist
            except SourceNotFoundException:
                continue
            # The search goes in order of source priority. So if a source variable exists, whether or not it's null,
            # that's the translation.
            return result
        raise SourceNotFoundException

    # TODO: Find some strategy, maybe involving named keyword arguments, to not include unused parameters
    # TODO: Find out what types "parent" is allowed to be
    def translate_folder(self, variable_id: str, variable: Variable, document: Dict, parent):
        """Translate for folders"""
        # Just translate all variables in the folder
        candidate: Dict = self(document, variable_id, parent)

        # If the resulting dictionary is empty, none of the children were found, so don't include the folder at all.
        if len(candidate) == 0:
            raise SourceNotFoundException
        return candidate

    # TODO Find out all the classes "parent" can take
    def translate_list(self, variable_id: str, variable: Variable, document: Dict, parent):
        """Translate for lists"""
        if variable.sources is None or len(variable.sources) == 0:
            raise SourceNotFoundException
        results = []
        # We have to restrict the sources to the descendants of parent
        # TODO Detect a case where this happens so I can figure out what it means
        parent_source = None
        if parent:
            parent_source = variable.track.source[parent]
        # The resulting list is the concatenation of all the translations,
        # source by source
        for source in variable.sources:
            if parent_source and not parent_source.check_ancestor(source):
                continue
            # get the document values for the current source
            try:
                list_source = self.find_in_document(source, document, parent)
            except SourceNotFoundException:
                continue
            if list_source is None:
                raise RuntimeError("I don't think this should be possible, because SourceNotFoundException replaced it")
            # sometimes lists with one element are represented as folders
            if isinstance(list_source, dict):
                list_source = [list_source]
            for value in list_source:
                # translate the values in the list one by one and add them to
                # the result
                # noinspection PyTypeChecker
                matches: Dict = self(value, variable_id, source)
                results.append(matches)
        return results

    def translate_named_list(self, variable_id, variable, document, parent):
        """Translate function for named lists (similar to python dicts), the
        logic is almost the same as for lists but taking care of the keys.
        Raises ValueError on duplicate keys"""
        if variable.sources is None or len(variable.sources) == 0:
            raise SourceNotFoundException
        results = {}
        # We have to restrict the sources to the descendants of parent
        parent_source = None
        if parent:
            parent_source = variable.track.source[parent]
        for source in variable.sources:
            if parent_source and not parent_source.check_ancestor(source):
                continue
            list_source = self.find_in_document(source, document, parent)
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

    def get_translate_function(self, variable: "Variable"):
        """Python polymorphism"""
        if isinstance(variable, NamedList):
            return self.translate_named_list
        elif isinstance(variable, List):
            return self.translate_list
        elif isinstance(variable, Folder):
            return self.translate_folder
        else:
            return self.translate_generic

    # TODO Figure out what classes parent and source_parent are ever allowed to be.
    def __call__(self, document: Dict, parent='', source_parent=''):
        output_document: Dict = {}
        # Translate all variables with the same parent
        children: Dict = self.target_variables_by_parent[parent]
        for variable_id, variable in children.items():  # type: str, "Variable"
            try:
                translate = self.get_translate_function(variable)
                result: Optional[Any] = translate(variable_id, variable, document, source_parent)
                output_document[variable.name] = result
            except SourceNotFoundException:
                continue
            except Exception as e:
                if self.failsafe:
                    logging.error('Error translating variable %s', variable_id)
                    continue
                else:
                    raise e
        return output_document
