import unittest
from dwork.dataset.pandas import PandasDataset
from .test_expressions import load_ds

class DatasetTest(unittest.TestCase):

    def test_filtering(self):
        ds = load_ds()
        dsf = ds[ds["Age"] > 30]
        assert ds.len().true() > dsf.len().true()
        assert dsf.len().true() == 563