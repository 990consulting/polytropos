from collections.abc import Callable, Iterable
from typing import Optional, Set


class SubjectValidator:
    """Subject validator class: this is a descriptor that validates subjects in
    task steps"""
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

    def __set__(self, instance, value):
        for validator in self.validators:
            if not validator(value):
                raise ValueError(
                    f'Validation error for {self.name} with value {value}'
                )
        instance.__dict__[self.name] = value
