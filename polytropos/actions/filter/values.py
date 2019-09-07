from dataclasses import dataclass

from polytropos.actions.filter import Filter



@dataclass
class ContainerNotEmptyFilter(Filter):
    """This filter may be used for either filtering or narrowing.

    Filtering: Includes only records for which a container variable (Folder, List, or KeyedList) is present and has
    at least one value inside.

    Narrowing: Includes only periods for which a container variable (Folder, List, or KeyedList) is present and has
    at least one value inside. Immutable containers are not allowed in narrow-only mode and will raise an error."""
    pass

