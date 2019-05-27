from collections.abc import Callable
from typing import Optional, Set


class SubjectValidator:
    def __init__(self, validators=None,  **kwargs):
        self.validators = validators or []
        if 'data_type' in kwargs:
            self.validators.append(
                lambda value: isinstance(value, kwargs['data_type'])
            )

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        for validator in self.validators:
            if not validator(value):
                raise ValueError(
                    f'Validation error for {self.name} with value {value}'
                )
        instance.__dict__[self.name] = value
