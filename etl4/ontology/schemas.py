from marshmallow import Schema, validate, fields, validates, validates_schema, ValidationError
from typing import Set, Dict, Optional, List

DATA_TYPES: Set = {
    # Primitive types
    "Integer", "Text", "Decimal", "Unary", "Binary", "Currency", "Phone", "Email", "URL",

    # Container types
    "Folder", "List", "NamedList"
}

LIST_TYPES: Set = { "List", "NamedList" }

class VariableSchema(Schema):
    """A schema for deserializing JSON into Variable objects."""

    # The name of the node as it will appear in node paths.
    name = fields.Str(required=True)

    # The data type. Determines the object class into which the JSON will be deserialized.
    data_type = fields.Str(required=True, validate=validate.OneOf(DATA_TYPES))

    # The order in which this variable should be included in an observation. Sort order is scoped to the nesting level
    # of the variable.
    sort_order = fields.Integer(required=True, validate=lambda x: x >= 0)

    # Variable IDs of variables from a previous stage from which this variable's value may be directly derived, if any.
    sources = fields.List(fields.Str())

    # Container variable under which this variable is nested.
    parent = fields.Str()

    # For List and NamedList container variables only, sources for child variables relative to a root source.
    source_child_mappings = fields.Dict(
        keys=fields.Str(),
        values=fields.Dict(
            keys=fields.Str(),
            values=fields.List(fields.Str())
        )
    )

    # noinspection PyMethodMayBeStatic
    def validate_source_child_mappings(self, data: Dict):
        sources: Set = set(data.get("sources", set()) or set())
        source_child_mappings: Dict = data.get("source_child_mappings", {}) or {}
        scm_keys: Set = set(source_child_mappings.keys())
        if sources != scm_keys:
            raise ValidationError("Missing or unexpected source child mappings")

    @validates_schema()
    def validate_variable_schema(self, data: Dict):
        data_type: str = data["data_type"]
        source_child_mappings: Optional[Dict] = data.get("source_child_mappings")

        if data_type not in LIST_TYPES and source_child_mappings is not None:
            raise ValidationError("Only Lists and NamedLists can have source child mappings.")

        if data_type in LIST_TYPES:
            self.validate_source_child_mappings(data)
