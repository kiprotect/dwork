from dwork.dataset.pandas import PandasDataset
import pandas as pd
import os

datasets_path = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "datasets"
)


def main():
    filename = f"{datasets_path}/absenteeism_at_work.csv"
    df = pd.read_csv(filename, sep=";")
    ds = PandasDataset(df)

    for sample in ds.randomized_sample(exclude=["ID"], limit=100):
        print(sample)


if __name__ == "__main__":
    main()
