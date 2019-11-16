# -*- coding: utf-8 -*-

"""Console script for nsw_petrol_pricing."""
import pathlib
import sys

import click
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

DATASET_RESOURCES = ["0b99d4db-25ba-4095-ad99-8fb2858affa3"]
DOWNLOADED_RESOURCE_DIRNAME = pathlib.Path("../data")


@click.command()
def main(args=None):
    """Console script for nsw_petrol_pricing."""
    register_matplotlib_converters()

    for resource in DATASET_RESOURCES:
        click.echo("Processing {}".format(resource))
        df = pd.read_csv(DOWNLOADED_RESOURCE_DIRNAME / "{}.csv".format(resource))
        print(df.head())
        df["PriceUpdatedDate"] = pd.to_datetime(df["PriceUpdatedDate"], unit="s")

        plt.plot(df["PriceUpdatedDate"], df["Price"])
        # beautify the x-labels
        plt.gcf().autofmt_xdate()
        plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
