from typing import Any
from .expression import Expression
from ..dataschema import SchemaAttribute
from .helpers import is_dp, sensitivity, type


class Mod(Expression):
    pass


class Add(Expression):

    """
    Represents the sum of two expressions. Can only be calcualted for
    expressions that return numerical values.
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def type(self) -> SchemaAttribute:
        return self.left.type + self.right.type

    def sensitivity(self) -> Any:
        return max(self.left.sensitivity(), self.right.sensitivity())

    def is_dp(self) -> bool:
        return is_dp(self.left) and is_dp(self.right)

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.left.true() + self.right.true(), epsilon)

    def true(self) -> Any:
        return self.left.true() + self.right.true()
