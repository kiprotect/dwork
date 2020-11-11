import abc
from typing import Type, TypeVar
from .attribute import Attribute
from ..language.types import Type as DworkType
from ..dataschema import DataSchema

DataSchemaType = TypeVar("DataSchemaType", bound=DataSchema)


class Dataset:
    def __init__(self, schema: Type[DataSchemaType]):
        self.schema = schema(self)

    @abc.abstractmethod
    def len(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item: str) -> Attribute:
        raise NotImplementedError

    def type(self, column: str) -> DworkType:
        return self.schema.attributes[column]
