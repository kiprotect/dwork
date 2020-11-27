import abc
from typing import Type, TypeVar, Iterable, Union
from .attribute import Attribute
from ..language.types import Type as DworkType
from ..language.expression import Expression
from ..dataschema import DataSchema

DataSchemaType = TypeVar("DataSchemaType", bound=DataSchema)


class Dataset:
    def __init__(self, schema: Type[DataSchemaType]):
        self.schema = schema(self)

    @abc.abstractmethod
    def len(self) -> int:
        raise NotImplementedError

    def type(self, column: str) -> DworkType:
        return self.schema.attributes[column]

    @abc.abstractmethod
    def group_by(self, attributes: Iterable[Attribute]) -> "Dataset":
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(
        self, column_or_expression: Union[str, Expression]
    ) -> Union["Dataset", Attribute]:
        raise NotImplementedError
