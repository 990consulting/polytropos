import warnings
from typing import Any

warnings.warn("VariableValidator does not currently do anything.", SyntaxWarning)

class VariableValidator:
    """Used to validate that variables had required properties. Got in the way. Need to replace with a more holistic
     approach."""

    def __init__(self, **kwargs: Any):
        pass

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = value
