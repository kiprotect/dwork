import pandas as pd
import random
import operator
import math
from typing import Any, Union, Iterable
from .dataset import Dataset, GroupedDataset
from .attribute import Attribute, AttributeCondition, TrueAttribute
from ..language.types import Array, Type, Boolean
from ..mechanisms import geometric_noise, laplace_noise
from ..language.expression import Expression, ConditionalExpression
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

    def __ge__(self, other: Any) -> AttributeCondition:
        raise NotImplementedError

    def __le__(self, other: Any) -> AttributeCondition:
        raise NotImplementedError

    def __gt__(self, other: Any) -> AttributeCondition:
        return PandasAttributeCondition(self, operator.gt, other)

    def __lt__(self, other: Any) -> AttributeCondition:
        raise NotImplementedError

    def __eq__(self, other: Any) -> AttributeCondition:  # type: ignore[override]
        raise NotImplementedError

    def __ne__(self, other: Any) -> AttributeCondition:  # type: ignore[override]
        raise NotImplementedError


class PandasAttributeCondition(AttributeCondition):
    attribute: PandasAttribute
    operator: Any
    operand: Any

    def __init__(self, attribute: PandasAttribute, operator: Any, operand: Any):
        self.attribute = attribute
        self.operator = operator
        self.operand = operand

    def dp(self, epsilon: float) -> Any:
        raise NotImplementedError

    def sensitivity(self) -> Any:
        raise NotImplementedError

    def true(self) -> Any:
        return self.operator(self.attribute.true().series, self.operand)

    @property
    def type(self) -> Type:
        return Array(Boolean())


class GroupedPandasDataset(GroupedDataset):

    """
    Groups a dataset by one or several expressions. An expression can be a
    column name or a function. If a column name is given, a group will be
    generated for every value of that column.

    .. warning:: Be aware that grouping by attribute value might leak sensitive
       information about individuals in the dataset, as even the presence or
       absence of a particular group can provide information about an individual
       to an adversary. To mitigate this risk, the constructor of this class
       contains a `treshold` parameter whose function is explained below. Be
       careful when modifying this or unsetting this parameter, as it might
       lead to leakage of sensitive information.

    :param treshold: The minimum number of rows/datapoints that a formed group
      must have in order to qualify for inclusion. The treshold is evaluated
      against the differentially private row count of every group.
    :param epsilon: The $\epsilon$ value for the calculation of the row count
      of a group that is evaluated against the given treshold.

    .. warning:: Beware of setting a treshold to a very low value (e.g. 1 or 2)
      as this might leak sensitive information about the presence or absence of
      a given datapoint to an adversary. The reason for this is that currently
      we rely on the values of a given attribute that are present in the dataset
      to form groups, which can be problematic in combination with a low treshold.
      For example, if we choose a treshold of 1, adding a single datapoint with
      a given attribute value that was not present before to the dataset might
      produce a group with that value with a high probability, whereas when
      excluding this datapoint the probability of the group being generated
      is zero, causing the grouping to violate the differential privacy criterion.

    Future improvements:

    - Check that the chosen treshold in combination with the chosen epsilon
      actually produces differentially private groups and does not suffer from
      the negative inclusion problem mentioned above.

    """

    def __init__(self, dataset, treshold=10, epsilon=0.3, **kwargs):
        self.kwargs = kwargs
        self.dataset = dataset
        self._groups = []
        self._datasets = []
        for key, group in dataset.df.groupby(**kwargs):
            self._groups.append(key)
            self._datasets.append(PandasDataset(dataset.schema, group))

    @property
    def groups(self) -> Iterable[Any]:
        return self._groups

    @property
    def datasets(self) -> Iterable[Dataset]:
        return self._datasets


class PandasDataset(Dataset):
    def __init__(self, schema, df, *args, **kwargs):
        super().__init__(schema, *args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.df = df

    def len(self):
        return PandasLength(self)

    def __len__(self):
        return self.len()

    def group_by(self, **kwargs) -> GroupedDataset:
        return GroupedPandasDataset(self, **kwargs)

    def __getitem__(
        self, column_or_expression: Union[str, ConditionalExpression]
    ) -> Union["PandasDataset", PandasAttribute]:
        """
        :params column_or_expression: If a string, returns the attribute
          corresponding to the column named by the string. If an conditional
          expression, returns a dataset with all rows that match the condition.
        """
        if isinstance(column_or_expression, str):
            # this is a column name, we return a pandas attribute
            return PandasAttribute(self, column_or_expression)
        if not isinstance(column_or_expression, AttributeCondition):
            raise ValueError("not supported")
        # this is a filter expression, we return a dataset with all matching rows
        return PandasDataset(
            self.schema, self.df[column_or_expression.true()], *self.args, **self.kwargs
        )
