from .expression import Expression
from ..dataschema import SchemaAttribute, SumType
from typing import Any


class Function(Expression):
    pass


class Sum(Function):
    def __init__(self, expression):
        self.expression = expression

    @property
    def type(self) -> SchemaAttribute:
        return self.expression.type

    def dp(self, epsilon: float) -> Any:
        if not isinstance(self.type, SumType):
            raise ValueError("not a sum type")
        st = self.type.sum(len(self.expression.true()))
        return st.dp(self.expression.true().sum(), epsilon)

    def true(self) -> Any:
        return self.expression.true().sum()

    def sensitivity(self) -> Any:
        return 0
