from .expression import Expression
from ..dataset import Dataset
from ..mechanisms import geometric_noise
from .types import Type, Array, Integer, Float, Numeric
from typing import Any, Optional


class Function(Expression):
    pass


class Length(Function):
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    @property
    def type(self) -> Type:
        return Integer(min=0)

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
        it = self.expression.type.itemtype
        if not isinstance(it, Numeric):
            raise ValueError("expected a numeric type")
        return it.sum()

    def dp(self, epsilon: float) -> Any:
        if not isinstance(self.expression.type, Array):
            raise ValueError("not an array")
        tv = self.expression.true()
        # if differential privacy was applied on the level of the expression
        # already, we just return the true value
        if self.expression.is_dp():
            return tv
        st = self.expression.type.sum()
        return st.dp(tv.sum(), self.sensitivity(), epsilon)

    def true(self) -> Any:
        return self.expression.true().sum()

    def sensitivity(self, value: Optional[Any] = None) -> Any:
        """
        The sensitivity of a sum is given as the sensitivity of the expression
        that constitutes the sum.
        """
        return self.expression.sensitivity()
