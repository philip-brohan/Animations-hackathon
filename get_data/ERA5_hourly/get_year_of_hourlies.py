#!/usr/bin/env python

# Retrieve ERA5 hourly_values.
#  Every month in one year

import os
import cdsapi
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--variable", help="Variable name", type=str, required=True)
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/ERA5/hourly/reanalysis" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
args.opdir += "/%04d" % args.year
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)

c = cdsapi.Client()

dataset = "reanalysis-era5-single-levels"
for month in range(1, 13):
    os.makedirs("%s/%02d" % (args.opdir, month), exist_ok=True)
    opfile = "%s/%02d/%s.nc" % (args.opdir, month, args.variable)
    if os.path.isfile(opfile):
        print("File %s already exists, skipping download" % opfile)
        continue
    request = {
        "product_type": ["reanalysis"],
        "variable": [args.variable],
        "year": [args.year],
        "month": [month],
        "day": [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
            "31",
        ],
        "time": [
            "00:00",
            "01:00",
            "02:00",
            "03:00",
            "04:00",
            "05:00",
            "06:00",
            "07:00",
            "08:00",
            "09:00",
            "10:00",
            "11:00",
            "12:00",
            "13:00",
            "14:00",
            "15:00",
            "16:00",
            "17:00",
            "18:00",
            "19:00",
            "20:00",
            "21:00",
            "22:00",
            "23:00",
        ],
        "data_format": "netcdf",
        "download_format": "unarchived",
    }

    print("Downloading %s for %04d-%02d" % (args.variable, args.year, month))
    c.retrieve(dataset, request).download(opfile)
