# Functions to load ERA5 Hourly data

import os
import iris
from iris.util import squeeze
import iris.coord_systems
import numpy as np

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# ERA5 data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
cs_ERA5 = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = cs_ERA5
    cbe.coord("longitude").coord_system = cs_ERA5


def get_land_mask():
    # Load the land mask
    fname = "%s/ERA5/land_mask.nc" % os.getenv("SCRATCH")
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    land_mask = squeeze(iris.load_cube(fname))
    # Set data to 1 for land, 0 for sea
    land_mask.data.data[land_mask.data.mask] = 0
    land_mask.data.data[~land_mask.data.mask] = 1
    add_coord_system(land_mask)
    return land_mask


def load(
    variable="total_precipitation",
    year=None,
    month=None,
    day=None,
    hour=None,
    constraint=None,
    grid=None,
):
    if year is None or month is None or day is None or hour is None:
        raise Exception("Year, month, day, and hour must be specified")
    fname = "%s/ERA5/hourly/reanalysis/%04d/%02d/%s.nc" % (
        os.getenv("SCRATCH"),
        year,
        month,
        variable,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(
        time=lambda cell: cell.point.day == day and cell.point.hour == hour
    )
    varC = iris.load_cube(fname, ftt)
    # Get rid of unnecessary height dimensions
    if len(varC.data.shape) == 3:
        varC = varC.extract(iris.Constraint(expver=1))
    add_coord_system(varC)
    varC.long_name = variable
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Nearest())
    if constraint is not None:
        varC = varC.extract(constraint)
    return varC
