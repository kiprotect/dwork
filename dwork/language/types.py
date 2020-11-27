from ..mechanisms import laplace_noise, geometric_noise
from typing import Optional, Union, Any
import math
import abc

maxint = int(2e31 - 1)


class Type:
    def __init__(self):
        pass

    @abc.abstractmethod
    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        raise NotImplementedError


class Numeric(Type):
    @abc.abstractmethod
    def __add__(self, other: "Numeric") -> "Numeric":
        raise NotImplementedError

    @abc.abstractmethod
    def __mul__(self, other: "Numeric") -> "Numeric":
        raise NotImplementedError

    @abc.abstractmethod
    def __sub__(self, other: "Numeric") -> "Numeric":
        raise NotImplementedError

    @abc.abstractmethod
    def __truediv__(self, other: "Numeric") -> "Numeric":
        raise NotImplementedError

    @abc.abstractmethod
    def __floordiv__(self, other: "Numeric") -> "Numeric":
        raise NotImplementedError

    @abc.abstractmethod
    def sum(self) -> "Numeric":
        raise NotImplementedError

    @property
    def range(self) -> Any:
        return self.max - self.min

    @property
    def absmin(self) -> Any:
        return min(abs(self.min), abs(self.max))

    @property
    def absmax(self) -> Any:
        return max(abs(self.min), abs(self.max))

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

    def __add__(self, other: Numeric) -> Numeric:
        if isinstance(other, Array):
            other_type: Union[Numeric, Numeric] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Numeric):
            raise ValueError("cannot add these types")
        return Array(self.type + other_type)

    def __sub__(self, other: Numeric) -> Numeric:
        if isinstance(other, Array):
            other_type: Union[Numeric, Numeric] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Numeric):
            raise ValueError("cannot add these types")
        return Array(self.type - other_type)

    def __truediv__(self, other: Numeric) -> Numeric:
        if isinstance(other, Array):
            other_type: Union[Numeric, Numeric] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Numeric):
            raise ValueError("cannot divide these types")
        return Array(self.type / other_type)

    def __floordiv__(self, other: Numeric) -> Numeric:
        if isinstance(other, Array):
            other_type: Union[Numeric, Numeric] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Numeric):
            raise ValueError("cannot divide these types")
        return Array(self.type // other_type)

    def __mul__(self, other: Numeric) -> Numeric:
        if isinstance(other, Array):
            other_type: Union[Numeric, Numeric] = other.type
        else:
            other_type = other
        if not isinstance(other_type, Numeric):
            raise ValueError("cannot multiply these types")
        return Array(self.type * other_type)

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        raise NotImplementedError

    def sum(self) -> Numeric:
        if not isinstance(self.type, Numeric):
            raise ValueError("underlying type is not Numeric")
        return self.type.sum()


class Integer(Numeric):
    """
    Represents integer data
    """

    def __sub__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a - b
        """
        if isinstance(other, Array):
            return Array(self - other.type)
        return Integer()

    def __mul__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a * b
        """
        if isinstance(other, Array):
            return Array(self * other.type)
        return Integer()

    def __truediv__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a / b
        """
        if isinstance(other, Array):
            return Array(self / other.type)
        return Integer()

    def __floordiv__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a // b
        """
        if isinstance(other, Array):
            return Array(self // other.type)
        return Integer()

    def __init__(self, min: Optional[int] = -maxint, max: Optional[int] = maxint):
        self._min = min
        self._max = max

    @property
    def min(self) -> Any:
        return self._min

    @property
    def max(self) -> Any:
        return self._max

    def __add__(self, other: Numeric) -> Numeric:
        if not isinstance(other, Numeric):
            raise ValueError("can only add numeric types")
        if isinstance(other, Array):
            return Array(other.type + self)
        return Integer(
            int(math.floor(self.min + other.min)), int(math.ceil(self.max + other.max))
        )

    def sum(self) -> "Integer":
        return Integer()

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        return min(
            max(
                value + geometric_noise(epsilon, symmetric=True) * sensitivity, self.min
            ),
            self.max,
        )

    type = int


class Float(Numeric):
    """
    Represents floating point data
    """

    def __mul__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a / b
        """
        if isinstance(other, Array):
            return Array(self * other.type)
        return Float()

    def __sub__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a / b
        """
        if isinstance(other, Array):
            return Array(other.type - self)
        return Float(self.min - other.max, self.max - other.min)

    def __truediv__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a / b
        """
        if isinstance(other, Array):
            return Array(self / other.type)
        return Float()

    def __floordiv__(self, other: Numeric) -> Numeric:
        """
        Returns the type of a / b
        """
        if isinstance(other, Array):
            return Array(self // other.type)
        return Float()

    def __init__(
        self, min: Optional[float] = float("-inf"), max: Optional[float] = float("inf")
    ):
        self._min = min
        self._max = max

    @property
    def min(self) -> Any:
        return self._min

    @property
    def max(self) -> Any:
        return self._max

    def sum(self) -> Numeric:
        return Float()

    def __add__(self, other: Numeric) -> Numeric:
        if not isinstance(other, Numeric):
            raise ValueError("can only add numeric types")
        if isinstance(other, Array):
            return Array(self + other.type)
        return Float(self.min + other.min, self.max + other.max)

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        return min(
            max(value + laplace_noise(epsilon) * sensitivity, self.min), self.max
        )

    type = float


class Categorical(Type):
    """
    Represents categorical data
    """


class Boolean(Type):
    """
    Represents boolean data
    """

    def dp(self, value: Any, sensitivity: Any, epsilon: float) -> Any:
        """
        To do: implement randomized response-
        """
        raise NotImplementedError
