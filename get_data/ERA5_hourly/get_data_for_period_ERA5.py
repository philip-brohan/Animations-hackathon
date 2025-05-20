#!/usr/bin/env python

# Get monthly ERA5 data for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1940)
parser.add_argument("--endyear", type=int, required=False, default=2024)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
    for var in [
        "2m_temperature",
        "mean_sea_level_pressure",
        "total_precipitation",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind"
    ]:
        opfile = "%s/ERA5/hourly/reanalysis/%04d/%s.nc" % (
            os.getenv("SCRATCH"),
            year,
            var,
        )
        if not os.path.isfile(opfile):
            print(
                ("./get_year_of_hourlies.py --year=%d --variable=%s")
                % (
                    year,
                    var,
                )
            )
