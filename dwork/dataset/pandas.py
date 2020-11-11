import pandas as pd
import random
import math
from typing import Any
from .dataset import Dataset
from .attribute import Attribute
from ..language.types import Array, Type
from ..mechanisms import geometric_noise, laplace_noise
from ..language.expression import Expression
from ..language.functions import Length, Sum

import math


class PandasLength(Length):
    def true(self) -> Any:
        if not isinstance(self.dataset, PandasDataset):
            raise ValueError("expected a pandas dataset")
        return len(self.dataset.df)


class PandasAttribute(Attribute):
    def __init__(self, dataset, column):
        self.dataset = dataset
        self.column = column

    @property
    def type(self) -> Type:
        return Array(self.dataset.type(self.column))

    def len(self):
        """
        We use this unpythonic function to make all DP function calls look consistent.
        """
        return self.dataset.len()

    def sum(self):
        return Sum(self)

    def dp(self, epsilon: float) -> Any:
        raise NotImplementedError

    def true(self) -> Any:
        return self.dataset.df[self.column]

    def sensitivity(self) -> Any:
        dt = self.dataset.type(self.column)
        return dt.max - dt.min

    def __len__(self):
        return self.len()


class PandasDataset(Dataset):
    def __init__(self, schema, df, *args, **kwargs):
        super().__init__(schema, *args, **kwargs)
        self.df = df

    def len(self):
        return PandasLength(self)

    def __len__(self):
        return self.len()

    def __getitem__(self, item: str) -> PandasAttribute:
        return PandasAttribute(self, item)
