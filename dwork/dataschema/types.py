from .attribute import SchemaAttribute
from ..mechanisms import laplace_noise, geometric_noise
from typing import Optional, Union, Any
import math
import abc


class SumType:
    @abc.abstractmethod
    def sum(self, n: int) -> "SumType":
        raise NotImplementedError


class Integer(SchemaAttribute, SumType):
    """
    Represents integer data
    """

    def __init__(self, min: int, max: int, sensitivity: Optional[int] = None):
        self.min = min
        self.max = max
        if sensitivity is None:
            self._sensitivity = self.max - self.min
        else:
            self._sensitivity = sensitivity

    def __add__(self, other: Union["Float", "Integer"]) -> "Integer":
        sensitivity = int(max(self.sensitivity, int(math.ceil(other.sensitivity))))
        return Integer(
            int(math.floor(self.min + other.min)),
            int(math.ceil(self.max + other.max)),
            sensitivity,
        )

    def sum(self, n: int) -> "Integer":
        return Integer(self.min * n, self.max * n, self.sensitivity)

    def dp(self, value: Any, epsilon: float) -> Any:
        return max(
            self.min,
            min(
                self.max,
                value + geometric_noise(epsilon, symmetric=True) * self.sensitivity,
            ),
        )

    @property
    def sensitivity(self) -> int:
        return self._sensitivity

    type = int


class Float(SchemaAttribute, SumType):
    """
    Represents floating point data
    """

    def __init__(self, min: float, max: float, sensitivity: Optional[float] = None):
        self.min = min
        self.max = max
        if sensitivity is None:
            self._sensitivity = self.max - self.min
        else:
            self._sensitivity = sensitivity

    def sum(self, n: int) -> "Float":
        return Float(self.min * n, self.max * n, self.sensitivity)

    def __add__(self, other: Union["Float", Integer]) -> "Float":
        sensitivity = max(self.sensitivity, other.sensitivity)
        return Float(self.min + other.min, self.max + other.max, sensitivity)

    def dp(self, value: Any, epsilon: float) -> Any:
        return max(
            self.min, min(self.max, value + laplace_noise(epsilon) * self.sensitivity)
        )

    @property
    def sensitivity(self) -> float:
        return self._sensitivity

    type = float


class Categorical(SchemaAttribute):
    """
    Represents categorical data
    """


class Boolean(SchemaAttribute):
    """
    Represents boolean data
    """
