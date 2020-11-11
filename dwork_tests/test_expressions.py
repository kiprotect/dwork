import unittest
import pandas as pd
import os

from dwork.dataset.pandas import PandasDataset
from dwork.dataschema import DataSchema
from dwork.language.types import Integer, Float

datasets_path = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "examples/datasets"
)

class AbsenteeismSchema(DataSchema):
    Weight = Integer(min=0, max=200)
    Height = Integer(min=0, max=200)

def load_ds():
    filename = f"{datasets_path}/absenteeism_at_work.csv"
    df = pd.read_csv(filename, sep=";")
    ds = PandasDataset(AbsenteeismSchema, df)
    return ds

class ExpressionsTest(unittest.TestCase):

    def test_simple_sum(self):
        ds = load_ds()
        # we add two values together (which is nonsensical in this case)
        x = (ds["Weight"]+ds["Height"]).sum()
        assert not x.is_dp()

        tx = (ds.df["Weight"]+ds.df["Height"]).sum()
        # we make sure the exact value is what we expect
        assert tx == 185851

        # we make sure the exact value is identical to the expression value
        assert tx == x.true()

        # we make sure the 
        assert 183000 <= x.dp(0.5) <= 187000

        uniques = set()
        for i in range(10):
            xdp = x.dp(0.5)
            uniques.add(xdp)
            assert 183000 <= xdp <= 188000

        # we check that the DP mechanism does not always produce the same value
        # (this is not a proper DP test)
        assert len(uniques) >= 4

    def test_mean(self):
        ds = load_ds()
        # we add two values together (which is nonsensical in this case)
        x = ds["Weight"].sum()/ds.len()
        assert not x.is_dp()

        tx = ds.df["Weight"].sum()/len(ds.df)
        # we make sure the exact value is what we expect
        assert tx == 79.03513513513514

        # we make sure the exact value is identical to the expression value
        assert tx == x.true()

        # we make sure the sensitivity is lower than that of the original value
        assert x.sensitivity() == 0.2706359945872801

        uniques = set()
        for i in range(10):
            xdp = x.dp(0.5)
            uniques.add(xdp)
            assert 60 <= xdp <= 100

        # we check that the DP mechanism does not always produce the same value
        # (this is not a proper DP test)
        assert len(uniques) >= 5