#!/usr/bin/env python

# Retrieve a soil temperature file from ERA5-land

# This is just an easy way to get a high-resolution land mask for plotting

import os
import cdsapi

opdir = "%s/ERA5/" % os.getenv("SCRATCH")
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)

if not os.path.isfile("%s/land_mask.nc" % opdir):  # Only bother if we don't have it

    c = cdsapi.Client() 

    # Variable and date are arbitrary
    # Just want something that is only defined in land grid-cells.

    dataset = "reanalysis-era5-land-monthly-means"
    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["soil_temperature_level_1"],
        "year": ["2024"],
        "month": ["01"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived"
    }

    c.retrieve(dataset, request).download("%s/%s.nc" % (opdir, "land_mask"))

    # Use system call to run ncks on output file
    # To remove 'expver' variable (otherwise iris won't load it)
    # os.system(
    #     "ncks -O -C -x -v expver %s/%s.nc %s/%s.nc"
    #     % (opdir, "land_mask", opdir, "land_mask")
    # ) test
