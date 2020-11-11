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


class Divisible(Type):
    @abc.abstractmethod
    def __truediv__(self, other: "Divisible") -> "Divisible":
        raise NotImplementedError

    @abc.abstractmethod
    def __floordiv__(self, other: "Divisible") -> "Divisible":
        raise NotImplementedError


class Multipliable(Type):
    @abc.abstractmethod
    def __mul__(self, other: "Multipliable") -> "Multipliable":
        raise NotImplementedError


class Addable(Type):
    @abc.abstractmethod
    def __add__(self, other: "Addable") -> "Addable":
        raise NotImplementedError

    @abc.abstractmethod
    def sum(self, n: int) -> "Addable":
        raise NotImplementedError


class Subtractable(Type):
    @abc.abstractmethod
    def __sub__(self, other: "Subtractable") -> "Subtractable":
        raise NotImplementedError


class Numeric(Addable, Divisible, Subtractable, Multipliable):
    @abc.abstractproperty
    def min(self) -> Any:
        raise NotImplementedError

    @abc.abstractproperty
    def max(self) -> Any:
        raise NotImplementedError


class Array(Numeric):
    def __init__(self, type: Type):
        if not isinstance(type, Numeric):
            raise ValueError("array requires a numeric type")
        self.type = type

    @property
    def itemtype(self) -> Type:
        return self.type

    @property
    def min(self):
        return self.type.min

    @property
    def max(self):
        return self.type.max

    def __add__(self, other: Addable) -> Addable:
        if isinstance(other, Array):
            other_type: Union[Numeric, Addable] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Addable):
            raise ValueError("cannot add these types")
        return Array(self.type + other_type)

    def __sub__(self, other: Subtractable) -> Subtractable:
        if isinstance(other, Array):
            other_type: Union[Numeric, Subtractable] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Subtractable):
            raise ValueError("cannot add these types")
        return Array(self.type - other_type)

    def __truediv__(self, other: Divisible) -> Divisible:
        if isinstance(other, Array):
            other_type: Union[Numeric, Divisible] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Divisible):
            raise ValueError("cannot divide these types")
        return Array(self.type / other_type)

    def __floordiv__(self, other: Divisible) -> Divisible:
        if isinstance(other, Array):
            other_type: Union[Numeric, Divisible] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Divisible):
            raise ValueError("cannot divide these types")
        return Array(self.type // other_type)

    def __mul__(self, other: Multipliable) -> Multipliable:
        if isinstance(other, Array):
            other_type: Union[Numeric, Multipliable] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Multipliable):
            raise ValueError("cannot multiply these types")
        return Array(self.type * other_type)

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        raise NotImplementedError

    def sum(self, n: int) -> Addable:
        if not isinstance(self.type, Addable):
            raise ValueError("underlying type is not addable")
        return self.type.sum(n)


class Integer(Numeric):
    """
    Represents integer data
    """

    def __sub__(self, other: Subtractable) -> Subtractable:
        """
        Returns the type of a / b
        """
        return Integer()

    def __mul__(self, other: Multipliable) -> Multipliable:
        """
        Returns the type of a / b
        """
        return Integer()

    def __truediv__(self, other: Divisible) -> Divisible:
        """
        Returns the type of a / b
        """
        return Integer()

    def __floordiv__(self, other: Divisible) -> Divisible:
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

    def __add__(self, other: Addable) -> Addable:
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


class Float(Numeric):
    """
    Represents floating point data
    """

    def __mul__(self, other: Multipliable) -> Multipliable:
        """
        Returns the type of a / b
        """
        return Float()

    def __sub__(self, other: Subtractable) -> Subtractable:
        """
        Returns the type of a / b
        """
        return Float()

    def __truediv__(self, other: Divisible) -> Divisible:
        """
        Returns the type of a / b
        """
        return Float()

    def __floordiv__(self, other: Divisible) -> Divisible:
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

    def sum(self, n: int) -> Numeric:
        return Float(
            self.min * n if self.min is not None else None,
            self.max * n if self.max is not None else None,
        )

    def __add__(self, other: Addable) -> Addable:
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
