from dwork.dataset.pandas import PandasDataset
import pandas as pd
import os

datasets_path = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "datasets"
)


def main():
    filename = f"{datasets_path}/absenteeism_at_work.csv"
    df = pd.read_csv(filename, sep=";")
    ds = PandasDataset(df, epsilon=0.01)

    # This is slightly "unpythonic"...
    l = ds.len()

    # (ds['income'].sum()/ds.len()).get()

    # This actually retrieves the length
    print(l.get())

    # Examples that will soon be available:

    # Comparisons
    # ds['income'] > 10000

    # Expressions
    # ds['income']*2 + ds['taxes']

    # Filtering
    # ds[ds['income'] > 10000]

    # Functions
    # ds.min(), ds.max(), ds.sum(), ...


if __name__ == "__main__":
    main()
