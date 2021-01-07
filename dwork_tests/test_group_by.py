import unittest

from .test_expressions import load_ds

class GroupByTest(unittest.TestCase):

    def test_simple_group_by(self):
        ds = load_ds()
        dsg = ds.group_by(by=["Weight"])

        # to calculate an expression on grouped data, we need to ensure that
        # the grouping is identical. In the future we might support more
        # advanced grouping functionality, but to keep it easy we will only
        # allow operations that are performed on identically grouped datasets
        # for now, as this makes implementation much more straightforward.
        for ds in dsg.datasets:
            mean_heights = ds["Height"].sum()/ds.len()

            # this should return a list of differentially private mean heights,
            # grouped by weight.
            results = mean_heights.dp(0.5)
            print("True:", ds["Height"].sum().true()/ds.len().true())
            print("DP:", results)