from typing import Any
from .expression import Expression
from .types import Type, Addable, Subtractable, Multipliable, Divisible


class Mod(Expression):
    pass


class BinaryExpression(Expression):
    left: Expression
    right: Expression

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right


class TrueDiv(BinaryExpression):
    @property
    def type(self) -> Type:
        if not isinstance(self.left.type, Divisible) or not isinstance(
            self.right.type, Divisible
        ):
            raise ValueError("expected divisible arguments")
        return self.left.type / self.right.type

    def sensitivity(self) -> Any:
        """
        The sensitivity of a division operation is given as ls/(|rv|-rs), where
        ls is the sensitivity of the dividend (left value), rs is the sensitivity
        of the divisor (right value) and rv is the value of the divisor.
        """
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


class FloorDiv(BinaryExpression):
    @property
    def type(self) -> Type:
        if not isinstance(self.left.type, Divisible) or not isinstance(
            self.right.type, Divisible
        ):
            raise ValueError("expected divisible arguments")
        return self.left.type // self.right.type

    def sensitivity(self) -> Any:
        rv = self.right.true()
        return max(self.left.sensitivity(), self.right.sensitivity())

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() // self.right.true()


class Add(BinaryExpression):

    """
    Represents the sum of two expressions. Can only be calculated for
    expressions that return addable values.
    """

    @property
    def type(self) -> Type:
        if not isinstance(self.left.type, Addable) or not isinstance(
            self.right.type, Addable
        ):
            raise ValueError("expected addable arguments")
        return self.left.type + self.right.type

    def sensitivity(self) -> Any:
        return max(self.left.sensitivity(), self.right.sensitivity())

    def is_dp(self) -> bool:
        return self.left.is_dp() and self.right.is_dp()

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() + self.right.true()


class Mul(BinaryExpression):

    """
    Represents the product of two expressions. Can only be calculated for
    expressions that return multipliable values.
    """

    @property
    def type(self) -> Type:
        if not isinstance(self.left.type, Multipliable) or not isinstance(
            self.right.type, Multipliable
        ):
            raise ValueError("expected multipliable arguments")
        return self.left.type * self.right.type

    def sensitivity(self) -> Any:
        """
        The sensitivity of a multiplication is given as the maximum of
        |lv|*(|rv|+rs) and |rv|*(|lv|+ls).
        """
        ls = self.left.sensitivity()
        rs = self.right.sensitivity()
        rv = self.right.true()
        lv = self.left.true()
        return max(abs(lv) * (abs(rv) + rs), abs(rv) * (abs(lv) + ls))

    def is_dp(self) -> bool:
        return self.left.is_dp() and self.right.is_dp()

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() * self.right.true()


class Sub(BinaryExpression):

    """
    Represents the difference of two expressions. Can only be calculated for
    expressions that return subtractable values.
    """

    @property
    def type(self) -> Type:
        if not isinstance(self.left.type, Subtractable) or not isinstance(
            self.right.type, Subtractable
        ):
            raise ValueError("expected subtractable arguments")
        return self.left.type - self.right.type

    def sensitivity(self) -> Any:
        return max(self.left.sensitivity(), self.right.sensitivity())

    def is_dp(self) -> bool:
        return self.left.is_dp() and self.right.is_dp()

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.left.true() - self.right.true()
