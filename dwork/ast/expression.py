import abc
from typing import Any
from ..dataschema import SchemaAttribute


class Expression(abc.ABC):
    def __add__(self, right: "Expression") -> "Expression":
        from .operators import Add

        return Add(self, right)

    @abc.abstractproperty
    def type(self) -> SchemaAttribute:
        raise NotImplementedError

    @abc.abstractmethod
    def sensitivity(self) -> Any:
        raise NotImplementedError

    def is_dp(self) -> bool:
        """
        Returns `True` if the value of this expression already fulfills
        the DP property.
        """
        return False

    def sum(self) -> "Expression":
        """
        Returns the sum of an expression. Assumes that the expression is indexable.
        """
        from .functions import Sum

        return Sum(self)

    @abc.abstractmethod
    def true(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def dp(self, epsilon: float) -> Any:
        raise NotImplementedError
