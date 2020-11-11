from .expression import Expression
from ..dataset import Dataset
from ..mechanisms import geometric_noise
from .types import Type, Array, Integer, Float
from typing import Any, Optional


class Function(Expression):
    pass


class Length(Function):
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    @property
    def type(self) -> Type:
        return Integer(min=0, max=None)

    def sensitivity(self, value: Optional[Any] = None) -> Any:
        return 1

    def dp(self, epsilon: float) -> Any:
        return self.type.dp(self.true(), self.sensitivity(), epsilon)


class Sum(Function):
    def __init__(self, expression):
        self.expression = expression

    @property
    def type(self) -> Type:
        if not isinstance(self.expression.type, Array):
            raise ValueError("not an array")
        return self.expression.type.itemtype

    def dp(self, epsilon: float) -> Any:
        if not isinstance(self.expression.type, Array):
            raise ValueError("not an array")
        tv = self.expression.true()
        st = self.expression.type.sum(len(tv))
        return st.dp(tv.sum(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.expression.true().sum()

    def sensitivity(self, value: Optional[Any] = None) -> Any:
        return self.expression.sensitivity()
