import abc
from typing import Any


class SchemaAttribute:
    def __init__(self):
        pass

    @abc.abstractproperty
    def sensitivity(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def dp(self, value: Any, epsilon: float) -> Any:
        raise NotImplementedError
