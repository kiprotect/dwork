import abc
from typing import Type, TypeVar
from .attribute import Attribute
from ..ast.types import Type as DworkType
from ..dataschema import DataSchema

DataSchemaType = TypeVar("DataSchemaType", bound=DataSchema)


class Dataset:
    def __init__(self, schema: Type[DataSchemaType], epsilon: float = 0.5):
        self.schema = schema(self)
        self.epsilon = epsilon

    @abc.abstractmethod
    def len(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item: str) -> Attribute:
        raise NotImplementedError

    def type(self, column: str) -> DworkType:
        return self.schema.attributes[column]
