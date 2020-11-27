import pandas as pd
import random
import operator
import math
from typing import Any, Union
from .dataset import Dataset
from .attribute import Attribute, TrueAttribute
from ..language.types import Array, Type
from ..mechanisms import geometric_noise, laplace_noise
from ..language.expression import Expression
from ..language.functions import Length, Sum

import math


class PandasLength(Length):
    def true(self) -> Any:
        if not isinstance(self.dataset, PandasDataset):
            raise ValueError("expected a pandas dataset")
        return len(self.dataset.df)


class TruePandasAttribute(TrueAttribute):
    def __init__(self, series: pd.Series):
        self.series = series

    def __op__(self, op: Any, other: TrueAttribute) -> TrueAttribute:
        if not isinstance(other, (TruePandasAttribute, float, int)):
            raise ValueError("cannot add")
        if isinstance(other, TruePandasAttribute):
            return TruePandasAttribute(op(self.series, other.series))
        else:
            return TruePandasAttribute(op(self.series, other))

    def __add__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__radd__(other)

    def __radd__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__op__(operator.add, other)

    def __sub__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__rsub__(other)

    def __rsub__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__op__(operator.sub, other)

    def __mul__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__rmul__(other)

    def __rmul__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__op__(operator.mul, other)

    def __truediv__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__rtruediv__(other)

    def __rtruediv__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__op__(operator.truediv, other)

    def __floordiv__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__rfloordiv__(other)

    def __rfloordiv__(self, other: TrueAttribute) -> TrueAttribute:
        return self.__op__(operator.floordiv, other)

    def abs(self) -> Any:
        return TruePandasAttribute(self.series.abs())

    def __len__(self) -> int:
        return self.len()

    def len(self) -> int:
        return len(self.series)

    def sum(self) -> Any:
        return self.series.sum()

    def max(self) -> Any:
        return self.series.max()

    def min(self) -> Any:
        return self.series.min()


class PandasAttribute(Attribute):
    def __init__(self, dataset, column):
        self.dataset = dataset
        self.column = column

    @property
    def type(self) -> Type:
        return Array(self.dataset.type(self.column))

    def len(self):
        """
        We use this unpythonic function to make all DP function calls look consistent.
        """
        return self.dataset.len()

    def sum(self):
        return Sum(self)

    def dp(self, epsilon: float) -> Any:
        raise NotImplementedError

    def true(self) -> Any:
        return TruePandasAttribute(self.dataset.df[self.column])

    def sensitivity(self) -> Any:
        dt = self.dataset.type(self.column)
        return dt.max - dt.min

    def __len__(self):
        return self.len()


class PandasDataset(Dataset):
    def __init__(self, schema, df, *args, **kwargs):
        super().__init__(schema, *args, **kwargs)
        self.df = df

    def len(self):
        return PandasLength(self)

    def __len__(self):
        return self.len()

    def __getitem__(
        self, column_or_expression: Union[str, Expression]
    ) -> Union["PandasDataset", PandasAttribute]:
        if isinstance(column_or_expression, str):
            return PandasAttribute(self, column_or_expression)
        if isinstance(column_or_expression, Expression):
            raise ValueError("not supported")
