from .expression import Expression
from ..dataschema import SchemaAttribute
from typing import Any, Optional


def is_dp(value: Any) -> bool:
    if isinstance(value, Expression):
        return value.is_dp()
    # for non-expressions we always return True
    return True


def sensitivity(value: Any) -> Any:
    if isinstance(value, Expression):
        return value.sensitivity()
    return 0


def type(value: Any) -> Optional[SchemaAttribute]:
    if isinstance(value, Expression):
        return value.type
    return None
