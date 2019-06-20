from collections.abc import Callable, Iterable
from typing import Optional, Set

class VariableValidator:
    """A descriptor that validates that a variable meets specified criteria, then stores it as its variable ID"""
    def __init__(self, validators=None,  **kwargs):
        self.validators = validators or []
        if 'data_type' in kwargs:
            data_type = kwargs['data_type']
            if isinstance(data_type, Iterable):
                self.validators.append(
                    lambda value: any(isinstance(value, t) for t in data_type)
                )
            else:
                self.validators.append(
                    lambda value: isinstance(value, data_type)
                )

    def __set_name__(self, owner, name):
        self.name = name

    # TODO By the time __set__ is called, a string var_id has been converted into an actual Variable instance. __set__
    #  then validates it and turns it back into a var_id. This is convoluted, and a relic of a time before the Composite
    #  class. Now that Composite has access to the schema, it makes sense to perform the validation some other way.
    def __set__(self, instance, value):
        for validator in self.validators:
            valid: bool = validator(value)
            if not valid:
                raise ValueError(
                    f'Validation error for {self.name} with value {value}'
                )
        instance.__dict__[self.name] = value.var_id
