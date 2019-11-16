# -*- coding: utf-8 -*-

"""Console script for nsw_petrol_pricing."""
import csv
import pathlib
import sys
import datetime

import click
import urllib.parse
import requests

# Populated with
# curl https://data.nsw.gov.au/data/dataset/fuel-check | grep heading | grep -i price | cut -d/ -f6 | cut -d" " -f1 | sed 's/\(.*\)/    "\1,/'
DATASET_RESOURCES = [
    "e6827299-6f36-4ac2-85a0-07c27aaec4a9",
]
DOWNLOADED_RESOURCE_DIRNAME = pathlib.Path("../data")
DATASET_BASE_URL = "https://data.nsw.gov.au/data/datastore/dump/"
SERVO_ID_FIELDS = ("ServiceStationName", "Address", "Suburb", "Postcode", "Brand")


def is_valid_resource_line(line_dict):
    # Lines with an empty price, fuelcode or priceupdateddate are invalid
    # XXX - some lines have an empty brand... perhaps not a problem
    return all((line_dict["Price"], line_dict["FuelCode"], line_dict["PriceUpdatedDate"]))


def persist_single_resource(resource):
    r = requests.get(urllib.parse.urljoin(DATASET_BASE_URL, resource),
                     stream=True)
    r.raise_for_status()
    # _id,ServiceStationName,Address,Suburb,Postcode,Brand,FuelCode,PriceUpdatedDate,Price
    resource_reader = csv.DictReader(r.iter_lines(decode_unicode=True))

    # Setup current servo struct
    current_servo = {}
    for field in SERVO_ID_FIELDS:
        current_servo[field] = ""

    with open(DOWNLOADED_RESOURCE_DIRNAME / "{}.csv".format(resource), "w") as csvfile:
        resource_writer = csv.DictWriter(csvfile, resource_reader.fieldnames)
        resource_writer.writeheader()

        for line_dict in resource_reader:
            if not is_valid_resource_line(line_dict):
                # Print skipped?
                continue

            if not line_dict["ServiceStationName"]:
                # It's an extra fuel-code line. They don't repeat servo details
                #  so we inject them so each line is complete
                line_dict.update(current_servo)

            else:
                # It's a new servo, capture servo ID fields in case there are
                #  extra fuel-code lines
                for field in SERVO_ID_FIELDS:
                    current_servo[field] = line_dict[field]

            # Convert date field to seconds since epoch (ignore TZ) to make
            #  subsequent parsing easier
            line_dict["PriceUpdatedDate"] = round(datetime.datetime.strptime(
                line_dict["PriceUpdatedDate"], "%Y-%m-%dT%H:%M:%S").timestamp())

            # Fix precision in price field
            line_dict["Price"] = round(float(line_dict["Price"]), 1)
            resource_writer.writerow(line_dict)

        # print(line_dict)


@click.command()
def main(args=None):
    """Console script for nsw_petrol_pricing."""
    for resource in DATASET_RESOURCES:
        click.echo("Processing {}".format(resource))
        persist_single_resource(resource)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
