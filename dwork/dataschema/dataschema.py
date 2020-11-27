from ..language.types import Type
from typing import Dict


class DataSchemaMeta(type):
    def __init__(cls, name, bases, namespace):
        attributes = {}
        for key, value in namespace.items():
            if isinstance(value, Type):
                attributes[key] = value
        cls.attributes = attributes
        super().__init__(name, bases, namespace)


class DataSchema(metaclass=DataSchemaMeta):
    pass
