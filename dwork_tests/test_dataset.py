import unittest
from dwork.dataset.pandas import PandasDataset

class DatasetTest(unittest.TestCase):

    def test_dataset(self):
        ds = PandasDataset(True)