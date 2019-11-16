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
@click.option("--include", "-i", multiple=True)
def main(include):
    """Console script for nsw_petrol_pricing."""
    # TODO: don't join if there's no data for long enough?
    # TODO: n-day MA
    register_matplotlib_converters()

    for resource in DATASET_RESOURCES:
        click.echo("Processing {}".format(resource))
        df = pd.concat(
            map(pd.read_csv, DOWNLOADED_RESOURCE_DIRNAME.glob("*.csv"))
        )
        df = df[df.ServiceStationName.isin(include)]
        df = df[df.FuelCode == "E10"]
        df["PriceUpdatedDate"] = pd.to_datetime(df["PriceUpdatedDate"], unit="s")
        df.set_index("PriceUpdatedDate", inplace=True)
        df.groupby("ServiceStationName")["Price"].plot(
            legend=True,
            figsize=(160, 12))
        print(df.head())
        plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
