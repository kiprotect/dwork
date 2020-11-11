from ..mechanisms import laplace_noise, geometric_noise
from typing import Optional, Union, Any
import math
import abc


class Type:
    def __init__(self):
        pass

    @abc.abstractmethod
    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        raise NotImplementedError


class Addable:
    @abc.abstractmethod
    def __add__(self, other: Type) -> Type:
        raise NotImplementedError

    @abc.abstractmethod
    def sum(self, n: int) -> Type:
        raise NotImplementedError


class Numeric(Addable):
    @abc.abstractproperty
    def min(self) -> Any:
        raise NotImplementedError

    @abc.abstractproperty
    def max(self) -> Any:
        raise NotImplementedError


class Array(Type):
    def __init__(self, type: Type):
        self.type = type

    @property
    def itemtype(self) -> Type:
        return self.type

    def __add__(self, other: "Array") -> "Array":
        if not isinstance(other.type, Addable) or not isinstance(self.type, Addable):
            raise ValueError("cannot add these types")
        return Array(self.type + other.type)

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        raise NotImplementedError

    def sum(self, n: int) -> Type:
        if not isinstance(self.type, Addable):
            raise ValueError("underlying type is not addable")
        return self.type.sum(n)


class Integer(Type, Numeric):
    """
    Represents integer data
    """

    def __truediv__(self, other: Type) -> Type:
        """
        Returns the type of a / b
        """
        return Integer()

    def __init__(self, min: Optional[int] = None, max: Optional[int] = None):
        self._min = min
        self._max = max

    @property
    def min(self) -> Any:
        return self._min

    @property
    def max(self) -> Any:
        return self._max

    def __add__(self, other: Type) -> "Integer":
        if not isinstance(other, Numeric):
            raise ValueError("can only add numeric types")
        return Integer(
            int(math.floor(self.min + other.min))
            if self.min is not None and other.min is not None
            else None,
            int(math.ceil(self.max + other.max))
            if self.max is not None and other.max is not None
            else None,
        )

    def sum(self, n: int) -> "Integer":
        return Integer(
            self.min * n if self.min is not None else None,
            self.max * n if self.max is not None else None,
        )

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        v = value + geometric_noise(epsilon, symmetric=True) * sensitivity
        if self.min is not None:
            v = max(v, self.min)
        if self.max is not None:
            v = min(v, self.max)
        return v

    type = int


class Float(Type, Numeric):
    """
    Represents floating point data
    """

    def __truediv__(self, other: Type) -> Type:
        """
        Returns the type of a / b
        """
        return Float()

    def __init__(self, min: Optional[float] = None, max: Optional[float] = None):
        self._min = min
        self._max = max

    @property
    def min(self) -> Any:
        return self._min

    @property
    def max(self) -> Any:
        return self._max

    def sum(self, n: int) -> "Float":
        return Float(
            self.min * n if self.min is not None else None,
            self.max * n if self.max is not None else None,
        )

    def __add__(self, other: Type) -> "Float":
        if not isinstance(other, Numeric):
            raise ValueError("can only add numeric types")
        return Float(
            self.min + other.min
            if self.min is not None and other.min is not None
            else None,
            self.max + other.max
            if self.max is not None and other.max is not None
            else None,
        )

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        v = value + laplace_noise(epsilon) * sensitivity
        if self.min is not None:
            v = max(v, self.min)
        if self.max is not None:
            v = min(v, self.max)
        return v

    type = float


class Categorical(Type):
    """
    Represents categorical data
    """


class Boolean(Type):
    """
    Represents boolean data
    """
