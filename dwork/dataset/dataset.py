import abc
from typing import Type, TypeVar
from .attribute import Attribute
from ..dataschema import SchemaAttribute, DataSchema

DataSchemaType = TypeVar("DataSchemaType", bound=DataSchema)


class Dataset:
    def __init__(self, schema: Type[DataSchemaType], epsilon: float = 0.5):
        self.schema = schema(self)
        self.epsilon = epsilon

    @abc.abstractmethod
    def __getitem__(self, item: str) -> Attribute:
        raise NotImplementedError

    def type(self, column: str) -> SchemaAttribute:
        return self.schema.attributes[column]
