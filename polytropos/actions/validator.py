import warnings
warnings.warn("VariableValidator does not currently do anything.", SyntaxWarning)

class VariableValidator:
    """Used to validate that variables had required properties. Got in the way. Need to replace with a more holistic
     approach."""

    def __init__(self, validators=None,  **kwargs):
        pass

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
