from typing import Any
from .expression import Expression
from ..dataset.attribute import Attribute
from .types import Type, Numeric, Array


def numeric(type: Type) -> Numeric:
    if not isinstance(type, Numeric):
        raise ValueError("expected a numeric type")
    return type


class BinaryExpression(Expression):
    left: Expression
    right: Expression

    def __init__(self, left: Expression, right: Expression):
        if not isinstance(left.type, Numeric) or not isinstance(right.type, Numeric):
            raise ValueError("expected Numeric arguments")
        self.left = left
        self.right = right

    def dp(self, epsilon: float) -> Any:
        if self.is_dp():
            # if DP was applied on the leven of the individual operands we
            # simply return the true value.
            return self.true()
        return self.type.dp(self.true(), self.sensitivity(), epsilon)

    def is_dp(self) -> bool:
        return self.left.is_dp() and self.right.is_dp()


class TrueDiv(BinaryExpression):
    @property
    def type(self) -> Type:
        return numeric(self.left.type) / numeric(self.right.type)

    def sensitivity(self) -> Any:
        rs = self.right.sensitivity()
        ls = self.left.sensitivity()
        lb = self.left.true()
        rb = self.right.true()

        lt = numeric(self.left.type)
        rt = numeric(self.right.type)

        # minimum possible left value given the current base value
        lv_min = max(lb - ls, lt.min)
        # maximum possible left value given the current base value
        lv_max = min(lb + ls, lt.max)

        # minimum possible right value given the current base value
        rv_min = max(rb - rs, rt.min)
        # maximum possible right value given the current base value
        rv_max = min(rb + rs, rt.max)

        if rv_max > 0 and rv_min < 0 or rt.max > 0 and rt.min < 0:
            raise ValueError("infinite sensitivity")

        # both values are arrays
        if isinstance(lt, Array) and isinstance(rt, Array):
            return lt.absmax / rt.absmin
        # left value is array, right is scalar
        if isinstance(lt, Array):
            return lt.absmax / min(abs(rv_min), abs(rv_max))
        # right value is array, left is scalar
        if isinstance(rt, Array):
            return max(abs(lv_min), abs(lv_max)) / rt.absmin
        # both values are scalars
        return max(
            abs(lv_min / rv_min - lb / rb),
            abs(lv_max / rv_min - lb / rb),
            abs(lv_min / rv_max - lb / rb),
            abs(lv_max / rv_max - lb / rb),
        )

    def true(self) -> Any:
        return self.left.true() / self.right.true()


class FloorDiv(BinaryExpression):
    @property
    def type(self) -> Type:
        return numeric(self.left.type) // numeric(self.right.type)

    def sensitivity(self) -> Any:
        rs = self.right.sensitivity()
        ls = self.left.sensitivity()
        lb = self.left.true()
        rb = self.right.true()

        lt = numeric(self.left.type)
        rt = numeric(self.right.type)

        # minimum possible left value given the current base value
        lv_min = max(lb - ls, lt.min)
        # maximum possible left value given the current base value
        lv_max = min(lb + ls, lt.max)

        # minimum possible right value given the current base value
        rv_min = max(rb - rs, rt.min)
        # maximum possible right value given the current base value
        rv_max = min(rb + rs, rt.max)

        if rv_max > 0 and rv_min < 0 or rt.max > 0 and rt.min < 0:
            raise ValueError("infinite sensitivity")

        # both values are arrays
        if isinstance(lt, Array) and isinstance(rt, Array):
            return lt.absmax // rt.absmin
        # left value is array, right is scalar
        if isinstance(lt, Array):
            return lt.absmax // min(abs(rv_min), abs(rv_max))
        # right value is array, left is scalar
        if isinstance(rt, Array):
            return max(abs(lv_min), abs(lv_max)) // rt.absmin
        # both values are scalars
        return max(
            abs(lv_min // rv_min - lb // rb),
            abs(lv_max // rv_min - lb // rb),
            abs(lv_min // rv_max - lb // rb),
            abs(lv_max // rv_max - lb // rb),
        )

    def true(self) -> Any:
        return self.left.true() // self.right.true()


class Add(BinaryExpression):

    """
    Represents the sum of two expressions. Can only be calculated for
    expressions that return Numeric values.
    """

    @property
    def type(self) -> Type:
        return numeric(self.left.type) + numeric(self.right.type)

    def sensitivity(self) -> Any:
        return max(self.left.sensitivity(), self.right.sensitivity())

    def true(self) -> Any:
        return self.left.true() + self.right.true()


class Mul(BinaryExpression):

    """
    Represents the product of two expressions. Can only be calculated for
    expressions that return Numeric values.
    """

    @property
    def type(self) -> Type:
        return numeric(self.left.type) * numeric(self.right.type)

    def sensitivity(self) -> Any:
        lt = numeric(self.left.type)
        rt = numeric(self.right.type)

        rs = self.right.sensitivity()
        ls = self.left.sensitivity()

        if not isinstance(lt, Array):
            lb = self.left.true()
            # minimum possible left value given the current base value
            lv_min = min(lb + ls, lt.max)
            # maximum possible left value given the current base value
            lv_max = max(lb - ls, lt.min)
        if not isinstance(self.right.type, Array):
            rb = self.right.true()
            # minimum possible right value given the current base value
            rv_min = min(rb + rs, rt.max)
            # maximum possible right value given the current base value
            rv_max = max(rb - rs, rt.min)

        # both values are arrays
        if isinstance(lt, Array) and isinstance(rt, Array):
            return ls * rs
        # left value is array, right is scalar
        if isinstance(lt, Array):
            return ls * max(abs(rv_min), abs(rv_max))
        # right value is array, left is scalar
        if isinstance(rt, Array):
            return rs * max(abs(lv_min), abs(lv_max))
        # both values are scalar
        return max(
            abs(lv_min * rv_min - lb * rb),
            abs(lv_max * rv_min - lb * rb),
            abs(lv_min * rv_max - lb * rb),
            abs(lv_max * rv_max - lb * rb),
        )

    def true(self) -> Any:
        return self.left.true() * self.right.true()


class Sub(BinaryExpression):

    """
    Represents the difference of two expressions. Can only be calculated for
    expressions that return Numeric values.
    """

    @property
    def type(self) -> Type:
        return numeric(self.left.type) - numeric(self.right.type)

    def sensitivity(self) -> Any:
        return max(self.left.sensitivity(), self.right.sensitivity())

    def true(self) -> Any:
        return self.left.true() - self.right.true()
