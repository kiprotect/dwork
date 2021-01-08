from ..language.types import Type
from typing import Dict, Optional


class DataSchemaMeta(type):
    def __init__(cls, name, bases, namespace):
        attributes = {}
        for key, value in namespace.items():
            if isinstance(value, Type):
                attributes[key] = value
        if cls.names is not None:
            for key, name in cls.names.items():
                attributes[name] = attributes[key]
        cls.attributes = attributes
        super().__init__(name, bases, namespace)


class DataSchema(metaclass=DataSchemaMeta):

    names: Optional[Dict[str, str]] = None
