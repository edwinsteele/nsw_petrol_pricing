# -*- coding: utf-8 -*-

"""Console script for nsw_petrol_pricing."""
import csv
import datetime
import pathlib
import sys
import urllib.parse

import click
import requests

# Populated with
# curl https://data.nsw.gov.au/data/dataset/fuel-check | grep heading | grep -i price | cut -d/ -f6 | cut -d" " -f1 | sed 's/\(.*\)/    "\1,/'
DATASET_RESOURCES = [
    "6d0a644f-83d8-49b2-beef-4fb180e4f6d1",
    "efebafce-5ddf-4f85-9840-07654b01a7a2",
    "7b09946e-ffa8-45f0-90b9-36b90af6e510",
    "d8e32bc9-9561-4971-abd5-21862f50d60d",
    "2a7128ae-02fa-40f7-b9de-a75479ebc9e4",
    "30d9d13d-ff8e-4041-82a1-1aa909d38f65",
    "f6414eb2-26ac-405b-8d1c-79680074f851",
    "5ad2ad7d-ccb9-4bc3-819b-131852925ede",
    "28a5e738-5fae-4e74-84dd-20adf0488d86",
    "a23dc2e7-8ca7-422d-9603-6c5693374318",
    "dba9405e-ad7e-4280-b994-041485db0e88",
    "d59adf5e-bcf6-4b0c-82a6-41ac9ec9162a",
    "85f33d70-af2e-4c5a-ab03-122df9cbabe4",
    "f7564618-2d92-432e-96a8-c7a29643cf1d",
    "8b6a7a49-3cb2-4501-97dd-344ac0883ad6",
    "0b99d4db-25ba-4095-ad99-8fb2858affa3",
    "c153fe34-f1d6-4b8a-a8af-450ef2b1489b",
    "e3b17109-b7c1-42ae-b300-d51b22bfa129",
    "c6d703f0-d8e8-4cd1-b9ca-93f2b88ff604",
    "db965e99-58e8-4525-a773-eef75f1f45b5",
    "9e1bf09b-da1d-4a5d-8d77-fba1186f0845",
    "a6467ed9-0f27-422b-8206-7ff3c3102c48",
    "bbf8f397-6095-4f57-b8c8-470f8009b493",
    "aeaa246b-eb66-4909-bc0e-a2ffd45cf019",
    "f0a7dd58-2cb0-4d19-afc9-9f967cf01ab5",
    "90256a55-9b7c-4918-98fb-3cd21584efc6",
    "a315878d-7911-47e7-958f-a23ffd41851b",
    "974b7a60-da7e-45f1-9bf8-00fbac94aab3",
    "dac77da2-bffa-43dd-967a-791f0be4ed46",
    "0bbaca04-2e1f-4558-b363-faa1f931910f",
    "6d5fd229-0cf1-449b-ad4f-94e4fd875258",
    "f178c2aa-b73c-44d7-bfa9-5bc267744932",
    "67b6f587-a387-4e7f-91ad-1ad015b17e8b",
    "86d05995-bb3c-4b81-b4e6-89918cab4bc7",
    "a7939d02-685c-4e28-858e-a8733ba27998",
    "dbbecc70-c2b5-49c4-97ae-8d73f2cef0ca",
    "e6827299-6f36-4ac2-85a0-07c27aaec4a9",
    "323f7c5e-9d47-4708-ad06-9462ab306372",
    "efcbe322-d35f-4fba-8f8b-b073035cfad5",
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
    # A bunch of 2016 and 2018 months don't have csv formatted data (only excel)
    if not r.ok:
        click.echo("Error retrieving {} Code {} Reason: {}".format(
            resource, r.status_code, r.reason), err=True)
        return

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
