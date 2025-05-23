# Functions to load The ML precipitation data

import os
import iris
import iris.cube
import iris.coords
import iris.coord_systems
from iris.util import squeeze
import iris.coord_systems
import iris.util
import numpy as np
import cftime
import datetime

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# Coordinate system for the data
ML_cs = iris.coord_systems.RotatedGeogCS(
    37.5, 177.5, ellipsoid=iris.coord_systems.GeogCS(6371229.0)
)

# Central data directory
Ddir = "/data/users/backup/datadir/ben.booth/ML/UNET_output/Tests_Mar25"


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("grid_latitude").coord_system = ML_cs
    cbe.coord("grid_longitude").coord_system = ML_cs


# Make a higher-res cube on the same grid as the data for plotting
def plot_cube(resolution=0.025, xmin=357.75, xmax=363.25, ymin=-2.75, ymax=2.75):

    lat_values = np.arange(ymin, ymax + resolution, resolution)
    latitude = iris.coords.DimCoord(
        lat_values,
        standard_name="grid_latitude",
        units="degrees_north",
        coord_system=ML_cs,
    )
    lon_values = np.arange(xmin, xmax + resolution, resolution)
    longitude = iris.coords.DimCoord(
        lon_values,
        standard_name="grid_longitude",
        units="degrees_east",
        coord_system=ML_cs,
    )
    dummy_data = np.zeros((len(lat_values), len(lon_values)))
    plot_cube = iris.cube.Cube(
        dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]
    )
    return plot_cube


default_cube = plot_cube()


def get_land_mask(grid=default_cube):
    fname = "%s/fixed_fields/land_mask/opfc_global_2019.nc" % os.getenv("DATADIR")
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    land_mask = squeeze(iris.load_cube(fname))
    land_mask = land_mask.regrid(grid, iris.analysis.Linear())
    return land_mask


def load_daily(
    model="target",
    year=None,
    month=None,
    day=None,
    member=1,
    grid=default_cube,
):
    if year is None or month is None or day is None:
        raise Exception("Year, month, and day, must be specified")
    c1 = iris.Constraint(
        time=lambda cell: cell.point.year == year
        and cell.point.month == month
        and cell.point.day == day
    )
    c2 = iris.Constraint(member=lambda cell: cell.point == member)
    if model == "target":
        fname = "%s/predictions_mse_corrected_structure.nc" % Ddir
        c3 = iris.Constraint(cube_func=lambda cube: cube.name() == "target")
        varC = iris.load_cube(
            fname,
            c1 & c2 & c3,
        )
    elif model == "unet-mse":
        fname = "%s/predictions_mse_corrected_structure.nc" % Ddir
        c3 = iris.Constraint(cube_func=lambda cube: cube.name() == "prediction")
        varC = iris.load_cube(
            fname,
            c1 & c2 & c3,
        )
    elif model == "unet-asym":
        fname = "%s/predictions_emulasym_corrected_structure.nc" % Ddir
        c3 = iris.Constraint(cube_func=lambda cube: cube.name() == "prediction")
        varC = iris.load_cube(
            fname,
            c1 & c2 & c3,
        )
    elif model == "diffusion":
        fname = "%s/predictions-ensemble01-sample0_Diffusion.nc" % Ddir
        c2 = iris.Constraint()
        c3 = iris.Constraint(cube_func=lambda cube: cube.name() == "pred_pr")
        varC = iris.load_cube(
            fname,
            c1 & c2 & c3,
        )
        varC.coord("ensemble_member").points = 1  # Hackety hack
        varC = iris.util.squeeze(varC)
        varC.data *= 86400.0  # Convert from m/s to m/day
    else:
        raise Exception("Unknown model %s" % model)
    add_coord_system(varC)
    if grid is not None:  # Regrid, but mask out areas outside original grid
        lat_max = varC.coord("grid_latitude").points.max()
        lat_min = varC.coord("grid_latitude").points.min()
        lon_max = varC.coord("grid_longitude").points.max()
        lon_min = varC.coord("grid_longitude").points.min()
        varC = varC.regrid(grid, iris.analysis.Nearest())
        latlon = np.meshgrid(
            varC.coord("grid_longitude").points, varC.coord("grid_latitude").points
        )
        varC.data = np.ma.masked_where(
            (latlon[0] < lon_min)
            | (latlon[0] > lon_max)
            | (latlon[1] < lat_min)
            | (latlon[1] > lat_max),
            varC.data,
        )
    return varC


# Switch dates using cftime


def load(
    model="target",
    year=None,
    month=None,
    day=None,
    hour=None,
    member=1,
    grid=default_cube,
):
    if year is None or month is None or day is None or hour is None:
        raise Exception("Year, month, day, and hour must be specified")
    today = load_daily(model, year, month, day, member, grid)
    current_date = cftime.datetime(year, month, day, hour, calendar="360_day")
    if hour == 12:
        return today
    elif hour < 12:
        previous_day = current_date - datetime.timedelta(days=1)
        prev = load_daily(
            model,
            previous_day.year,
            previous_day.month,
            previous_day.day,
            member,
            grid,
        )
        f = iris.cube.CubeList([prev, today])
        f = f.merge_cube()
        interpolated = f.interpolate(
            [("time", current_date.replace(hour=hour))], iris.analysis.Linear()
        )
        return interpolated
    else:  # hour> 12
        next_day = current_date + datetime.timedelta(days=1)
        next = load_daily(
            model,
            next_day.year,
            next_day.month,
            next_day.day,
            member,
            grid,
        )
        f = iris.cube.CubeList([today, next])
        f = f.merge_cube()
        interpolated = f.interpolate(
            [("time", current_date.replace(hour=hour))], iris.analysis.Linear()
        )
        return interpolated


def load_3hr(
    model="target",
    year=None,
    month=None,
    day=None,
    hour=None,
    grid=default_cube,
):
    if year is None or month is None or day is None or hour is None:
        raise Exception("Year, month, and day, must be specified")
    fyr = year
    if month == 12 and (day > 1 or hour > 0):
        fyr = year + 1
    fname = (
        "/data/scratch/tomas.wetherell/create_dataset/01/3hrinst_dataset_%04d.nc" % fyr
    )
    c1 = iris.Constraint(
        time=lambda cell: cell.point.year == year
        and cell.point.month == month
        and cell.point.day == day
        and cell.point.hour == hour
    )
    if model == "target":
        c3 = iris.Constraint(cube_func=lambda cube: cube.name() == "precipitation_flux")
        varC = iris.load_cube(
            fname,
            c1 & c3,
        )
        varC = iris.util.squeeze(varC)
        varC.data = varC.data * 86400.0  # Convert from m/s to m/day
    else:
        raise Exception("Unknown model %s" % model)
    add_coord_system(varC)
    if grid is not None:  # Regrid, but mask out areas outside original grid
        lat_max = varC.coord("grid_latitude").points.max()
        lat_min = varC.coord("grid_latitude").points.min()
        lon_max = varC.coord("grid_longitude").points.max()
        lon_min = varC.coord("grid_longitude").points.min()
        varC = varC.regrid(grid, iris.analysis.Nearest())
        latlon = np.meshgrid(
            varC.coord("grid_longitude").points, varC.coord("grid_latitude").points
        )
        varC.data = np.ma.masked_where(
            (latlon[0] < lon_min)
            | (latlon[0] > lon_max)
            | (latlon[1] < lat_min)
            | (latlon[1] > lat_max),
            varC.data,
        )
    return varC


def load_3hr_i(
    model="target",
    year=None,
    month=None,
    day=None,
    hour=None,
    minute=0,
    grid=default_cube,
):
    if year is None or month is None or day is None or hour is None:
        raise Exception("Year, month, day, and hour must be specified")
    if hour % 3 == 0 and minute == 0:
        return load_3hr(model, year, month, day, hour, grid)
    if hour % 3 != 0:
        b_hour = hour - hour % 3
    else:
        b_hour = hour
    b_field = load_3hr(model, year, month, day, b_hour, grid)
    e_hour = b_hour + 3
    current_date = cftime.datetime(year, month, day, hour, minute, calendar="360_day")
    if e_hour == 24:
        e_hour = 0
        next_day = current_date + datetime.timedelta(days=1)
        year = next_day.year
        month = next_day.month
        day = next_day.day
    e_field = load_3hr(model, year, month, day, e_hour, grid)
    f = iris.cube.CubeList([b_field, e_field])
    f = f.merge_cube()
    interpolated = f.interpolate([("time", current_date)], iris.analysis.Linear())
    return interpolated
