from typing import Any
from .expression import Expression
from .types import Type, Numeric


class Mod(Expression):
    pass


class TrueDiv(Expression):
    @property
    def type(self) -> Type:
        return self.left.type / self.right.type

    def sensitivity(self) -> Any:
        """
        The sensitivity of a division operation is given as ls/(|rv|-rs), where
        ls is the sensitivity of the dividend (left value), rs is the sensitivity
        of the divisor (right value) and rv is the value of the divisor.
        """
        if not isinstance(self.left.type, Numeric) or not isinstance(
            self.right.type, Numeric
        ):
            raise ValueError("expected numeric arguments")
        ls = self.left.sensitivity()
        rs = self.right.sensitivity()
        rv = self.right.true()
        rm = abs(rv) - rs
        if rm <= 0:
            raise ValueError("infinite sensitivity")
        return ls / rm

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() / self.right.true()

    def __init__(self, left, right):
        self.left = left
        self.right = right


class FloorDiv(Expression):
    @property
    def type(self) -> Type:
        return self.left.type // self.right.type

    def sensitivity(self) -> Any:
        rv = self.right.true()
        return max(self.left.sensitivity(), self.right.sensitivity())

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() // self.right.true()

    def __init__(self, left, right):
        self.left = left
        self.right = right


class Add(Expression):

    """
    Represents the sum of two expressions. Can only be calcualted for
    expressions that return numerical values.
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def type(self) -> Type:
        return self.left.type + self.right.type

    def sensitivity(self) -> Any:
        return max(self.left.sensitivity(), self.right.sensitivity())

    def is_dp(self) -> bool:
        return self.left.is_dp() and self.right.is_dp()

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() + self.right.true()
