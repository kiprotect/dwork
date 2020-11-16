from ..language.expression import Expression
from typing import Any
import abc


class TrueAttribute:

    """
    Represents the true value of an attribute. Specialized classes inherit from
    this base class to implement common functionality like min/max/abs values,
    sum, length and arithmetic operations.

    Wrapping the real attribute types (like a pandas.Series object) is necessary
    as some sensitivity calculations require access to these values.
    """

    @abc.abstractmethod
    def abs(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def max(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def min(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def sum(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def len(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __add__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __sub__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __mul__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __truediv__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __floordiv__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __radd__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __rsub__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __rmul__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __rtruediv__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError

    @abc.abstractmethod
    def __rfloordiv__(self, other: Any) -> "TrueAttribute":
        raise NotImplementedError


class Attribute(Expression):
    pass
