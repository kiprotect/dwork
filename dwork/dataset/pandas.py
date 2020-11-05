import pandas as pd
from .dataset import Dataset
from .attribute import Attribute
from ..mechanisms.geometric import geometric_noise
from .pandas_helpers import (
    epsilon,
    epsilon_flip,
    discretize,
    randomize,
    sample_p,
    sample_p_breadth_first,
)
from ..expressions import Function
import math


class Length(Function):
    def __init__(self, dataset):
        self.dataset = dataset

    def get(self):
        return max(
            0,
            len(self.dataset.df)
            + geometric_noise(self.dataset.epsilon, symmetric=True),
        )


class PandasAttribute(Attribute):
    def __init__(self, dataset, column):
        self.dataset = dataset
        self.column = column

    def len(self):
        """
        We use this unpythonic function to make all DP function calls look consistent.
        """
        return self.dataset.len()

    def sum(self):
        pass

    def __len__(self):
        return self.len()


class PandasDataset(Dataset):
    def __init__(self, df, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = df

    def len(self):
        return Length(self)

    def __len__(self):
        return self.len()

    def randomized_sample(
        self,
        breadth_first=True,
        interleave=0.0,
        max_depth=3,
        min_depth=1,
        limit=None,
        method="flip",
        exclude=None,
        target=None,
    ):
        fds, mapping, reverse_mapping = discretize(self.df, exclude=exclude)
        pr = 0.5
        pf = 0.5
        flip = method == "flip"
        fdsr = randomize(fds, 0, pf, flip=flip)
        if breadth_first:
            return sample_p_breadth_first(
                mapping,
                reverse_mapping,
                fdsr,
                fds,
                pr,
                pf,
                flip=flip,
                forced_attributes=target,
                min_depth=min_depth,
                max_depth=max_depth,
                limit=limit,
                verbose=False,
                interleave=interleave,
            )
