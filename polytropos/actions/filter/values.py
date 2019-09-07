from dataclasses import dataclass

from polytropos.actions.filter import Filter

@dataclass
class HasAnySpecificValuesFilter(Filter):
    """OR logic for filtering and narrowing (may be used for either or both).

    Filtering: Includes only records that have ever had a period in which at least one of the specified fields had
    the specified value. If one of the specified values is an immutable value, having that value will cause the record
    to pass.

    Narrowing: Includes only periods in which at least one of the specified fields has the specified value. Immutable
    values count against all periods; i.e., if an immutable value matches, all periods will be included."""
    pass


@dataclass
class ContainerNotEmptyFilter(Filter):
    """This filter may be used for either filtering or narrowing.

    Filtering: Includes only records for which a container variable (Folder, List, or KeyedList) is present and has
    at least one value inside.

    Narrowing: Includes only periods for which a container variable (Folder, List, or KeyedList) is present and has
    at least one value inside. Immutable containers are not allowed in narrow-only mode and will raise an error."""
    pass

