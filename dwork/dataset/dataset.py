import abc
from typing import Type, TypeVar, Union, Iterable, Any
from .attribute import Attribute
from ..language.types import Type as DworkType
from ..language.expression import ConditionalExpression
from ..dataschema import DataSchema

DataSchemaType = TypeVar("DataSchemaType", bound=DataSchema)


class Dataset:

    """Models a dataset with multiple attributes and rows of data. Allows
    slicing by attribute and filtering and provides functions like `len` and
    `group_by` that can be used to generated grouped datasets.
    """

    def __init__(self, schema: Type[DataSchemaType]):
        self.schema = schema

    @abc.abstractmethod
    def len(self) -> int:
        raise NotImplementedError

    def type(self, column: str) -> DworkType:
        return self.schema.attributes[column]

    @abc.abstractmethod
    def group_by(self, **kwargs) -> "GroupedDataset":
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(
        self, column_or_expression: Union[str, ConditionalExpression]
    ) -> Union["Dataset", Attribute]:
        raise NotImplementedError


class GroupedDataset:

    """Groups a dataset using a number of expressions. Provides two functions
    that return the group attributes as well as the actual datasets.
    """

    @abc.abstractproperty
    def groups(self) -> Iterable[Any]:
        raise NotImplementedError

    @abc.abstractproperty
    def datasets(self) -> Iterable[Dataset]:
        raise NotImplementedError
