#!/usr/bin/env python

# Atmospheric state - near-surface wind and precip.

import os
import sys
from get_data.ERA5_hourly.ERA5_hourly import load, get_land_mask
import datetime
import pickle

import iris
import numpy as np

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import cmocean

from pandas import qcut

# Fix dask SPICE bug
import dask

dask.config.set(scheduler="single-threaded")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument(
    "--hour", help="Time of day (0 to 23.99)", type=float, required=True
)
parser.add_argument(
    "--pole_latitude",
    help="Latitude of projection pole",
    default=90,
    type=float,
    required=False,
)
parser.add_argument(
    "--pole_longitude",
    help="Longitude of projection pole",
    default=180,
    type=float,
    required=False,
)
parser.add_argument(
    "--npg_longitude",
    help="Longitude of view centre",
    default=0,
    type=float,
    required=False,
)
parser.add_argument(
    "--zoom",
    help="Scale factor for viewport (1=global)",
    default=1,
    type=float,
    required=False,
)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/AnimH/visualizations/ERA+SYCLoPS" % os.getenv("SCRATCH"),
    type=str,
    required=False,
)
parser.add_argument(
    "--zfile",
    help="Noise pickle file name",
    default="%s/AnimH/visualizations/z.pkl" % os.getenv("SCRATCH"),
    type=str,
    required=False,
)
parser.add_argument(
    "--debug",
    action="store_true",
)

args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)


dte = datetime.datetime(
    args.year, args.month, args.day, int(args.hour), int(args.hour % 1 * 60)
)


# Remap the precipitation to standardise the distribution
# Normalise a precip field to fixed quantiles
def normalise_precip(p):
    res = p.copy()
    res.data[res.data <= 6.68e-5] = 0.79
    res.data[res.data < 7.77e-5] = 0.81
    res.data[res.data < 9.25e-5] = 0.83
    res.data[res.data < 1.11e-4] = 0.85
    res.data[res.data < 1.35e-4] = 0.87
    res.data[res.data < 1.68e-4] = 0.89
    res.data[res.data < 2.16e-4] = 0.91
    res.data[res.data < 2.94e-4] = 0.93
    res.data[res.data < 4.30e-4] = 0.95
    res.data[res.data < 7.11e-4] = 0.97
    res.data[res.data < 0.1] = 0.99
    return res


u10m = load("10m_u_component_of_wind", dte.year, dte.month, dte.day, dte.hour)
v10m = load("10m_v_component_of_wind", dte.year, dte.month, dte.day, dte.hour)
precip = load("total_precipitation", dte.year, dte.month, dte.day, dte.hour)
precip = normalise_precip(precip)

mask = get_land_mask()

# Define the figure (page size, background color, resolution, ...
fig = Figure(
    figsize=(19.2 * 2, 10.8 * 2),  # Width, Height (inches)
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,  # Don't draw a frame
    subplotpars=None,
    tight_layout=None,
)
fig.set_frameon(False)
# Attach a canvas
canvas = FigureCanvas(fig)

# Projection for plotting
cs = iris.coord_systems.RotatedGeogCS(
    args.pole_latitude, args.pole_longitude, args.npg_longitude
)


def plot_cube(resolution, xmin, xmax, ymin, ymax):

    lat_values = np.arange(ymin, ymax + resolution, resolution)
    latitude = iris.coords.DimCoord(
        lat_values, standard_name="latitude", units="degrees_north", coord_system=cs
    )
    lon_values = np.arange(xmin, xmax + resolution, resolution)
    longitude = iris.coords.DimCoord(
        lon_values, standard_name="longitude", units="degrees_east", coord_system=cs
    )
    dummy_data = np.zeros((len(lat_values), len(lon_values)))
    plot_cube = iris.cube.Cube(
        dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]
    )
    return plot_cube


# Make the wind noise
def wind_field(uw, vw, zf, sequence=None, iterations=50, epsilon=0.003, sscale=1):
    # Random field as the source of the distortions
    z = pickle.load(open(zf, "rb"))
    z = z.regrid(uw, iris.analysis.Linear())
    (width, height) = z.data.shape
    # Each point in this field has an index location (i,j)
    #  and a real (x,y) position
    xmin = np.min(uw.coords()[0].points)
    xmax = np.max(uw.coords()[0].points)
    ymin = np.min(uw.coords()[1].points)
    ymax = np.max(uw.coords()[1].points)

    # Convert between index and real positions
    def i_to_x(i):
        return xmin + (i / width) * (xmax - xmin)

    def j_to_y(j):
        return ymin + (j / height) * (ymax - ymin)

    def x_to_i(x):
        return np.minimum(
            width - 1,
            np.maximum(0, np.floor((x - xmin) / (xmax - xmin) * (width - 1))),
        ).astype(int)

    def y_to_j(y):
        return np.minimum(
            height - 1,
            np.maximum(0, np.floor((y - ymin) / (ymax - ymin) * (height - 1))),
        ).astype(int)

    i, j = np.mgrid[0:width, 0:height]
    x = i_to_x(i)
    y = j_to_y(j)
    # Result is a distorted version of the random field
    result = z.copy()
    # Repeatedly, move the x,y points according to the vector field
    #  and update result with the random field at their locations
    ss = uw.copy()
    ss.data = np.sqrt(uw.data**2 + vw.data**2)
    if sequence is not None:
        startsi = np.arange(0, iterations, 3)
        endpoints = np.tile(startsi, 1 + (width * height) // len(startsi))
        endpoints += sequence % iterations
        endpoints[endpoints >= iterations] -= iterations
        startpoints = endpoints - 25
        startpoints[startpoints < 0] += iterations
        endpoints = endpoints[0 : (width * height)].reshape(width, height)
        startpoints = startpoints[0 : (width * height)].reshape(width, height)
    else:
        endpoints = iterations + 1
        startpoints = -1
    for k in range(iterations):
        x += epsilon * vw.data[i, j]
        x[x > xmax] = xmax
        x[x < xmin] = xmin
        y += epsilon * uw.data[i, j]
        y[y > ymax] = y[y > ymax] - ymax + ymin
        y[y < ymin] = y[y < ymin] - ymin + ymax
        i = x_to_i(x)
        j = y_to_j(y)
        update = z.data * ss.data / sscale
        update[(endpoints > startpoints) & ((k > endpoints) | (k < startpoints))] = 0
        update[(startpoints > endpoints) & ((k > endpoints) & (k < startpoints))] = 0
        result.data[i, j] += update
    return result


wind_pc = plot_cube(
    0.2, -180 / args.zoom, 180 / args.zoom, -90 / args.zoom, 90 / args.zoom
)
rw = iris.analysis.cartography.rotate_winds(u10m, v10m, cs)
u10m = rw[0].regrid(wind_pc, iris.analysis.Linear())
v10m = rw[1].regrid(wind_pc, iris.analysis.Linear())
seq = (dte - datetime.datetime(2000, 1, 1)).total_seconds() / 3600
wind_noise_field = wind_field(
    u10m, v10m, args.zfile, sequence=int(seq * 5), epsilon=0.01
)

# Define an axes to contain the plot. In this case our axes covers
#  the whole figure
ax = fig.add_axes([0, 0, 1, 1])
ax.set_axis_off()  # Don't want surrounding x and y axis
ax.add_patch(  # Background
    Rectangle((-180, -90), 360, 180, facecolor=(0.9, 0.9, 0.9, 1), fill=True, zorder=1)
)

# Lat and lon range (in rotated-pole coordinates) for plot
ax.set_xlim(-180 / args.zoom, 180 / args.zoom)
ax.set_ylim(-90 / args.zoom, 90 / args.zoom)
ax.set_aspect("auto")

# Background
ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=(0.6, 0.6, 0.6, 1), fill=True, zorder=1))

# Draw lines of latitude and longitude
for lat in range(-90, 95, 5):
    lwd = 0.75
    x = []
    y = []
    for lon in range(-180, 181, 1):
        rp = iris.analysis.cartography.rotate_pole(
            np.array(lon), np.array(lat), args.pole_longitude, args.pole_latitude
        )
        nx = rp[0] + args.npg_longitude
        if nx > 180:
            nx -= 360
        ny = rp[1]
        if len(x) == 0 or (abs(nx - x[-1]) < 10 and abs(ny - y[-1]) < 10):
            x.append(nx)
            y.append(ny)
        else:
            ax.add_line(
                Line2D(x, y, linewidth=lwd, color=(0.4, 0.4, 0.4, 1), zorder=10)
            )
            x = []
            y = []
    if len(x) > 1:
        ax.add_line(Line2D(x, y, linewidth=lwd, color=(0.4, 0.4, 0.4, 1), zorder=10))

for lon in range(-180, 185, 5):
    lwd = 0.75
    x = []
    y = []
    for lat in range(-90, 90, 1):
        rp = iris.analysis.cartography.rotate_pole(
            np.array(lon), np.array(lat), args.pole_longitude, args.pole_latitude
        )
        nx = rp[0] + args.npg_longitude
        if nx > 180:
            nx -= 360
        ny = rp[1]
        if len(x) == 0 or (abs(nx - x[-1]) < 10 and abs(ny - y[-1]) < 10):
            x.append(nx)
            y.append(ny)
        else:
            ax.add_line(
                Line2D(x, y, linewidth=lwd, color=(0.4, 0.4, 0.4, 1), zorder=10)
            )
            x = []
            y = []
    if len(x) > 1:
        ax.add_line(Line2D(x, y, linewidth=lwd, color=(0.4, 0.4, 0.4, 1), zorder=10))

# Plot the land mask
mask_pc = plot_cube(
    0.05, -180 / args.zoom, 180 / args.zoom, -90 / args.zoom, 90 / args.zoom
)
mask = mask.regrid(mask_pc, iris.analysis.Linear())
lats = mask.coord("latitude").points
lons = mask.coord("longitude").points
ax.imshow(
    mask.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=matplotlib.colors.ListedColormap(((0.4, 0.4, 0.4, 0), (0.4, 0.4, 0.4, 1))),
    vmin=0,
    vmax=1,
    alpha=1.0,
    zorder=20,
    origin="lower",
    aspect="auto",
)


# Plot the Wind
wind_pc = plot_cube(
    0.05, -180 / args.zoom, 180 / args.zoom, -90 / args.zoom, 90 / args.zoom
)
wscale = 200
s = wind_noise_field.data.shape
wind_noise_field.data = (
    qcut(
        wind_noise_field.data.flatten(), wscale, labels=False, duplicates="drop"
    ).reshape(s)
    - (wscale - 1) / 2
)

# Plot as a colour map
wnf = wind_noise_field.regrid(wind_pc, iris.analysis.Linear())
t2m_img = ax.imshow(
    wnf.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=cmocean.cm.gray,
    alpha=0.6,
    zorder=100,
    vmin=-150,
    vmax=150,
    origin="lower",
    aspect="auto",
)

# Plot the precip
precip_pc = plot_cube(
    0.25, -180 / args.zoom, 180 / args.zoom, -90 / args.zoom, 90 / args.zoom
)
precip = precip.regrid(precip_pc, iris.analysis.Linear())
wnf = wind_noise_field.regrid(precip, iris.analysis.Linear())
precip.data[precip.data > 0.8] += wnf.data[precip.data > 0.8] / 3000
precip.data[precip.data < 0.8] = 0.8
cols = []
for ci in range(100):
    cols.append([0.0, 0.3, 0.0, ci / 100])
precip_img = ax.imshow(
    precip.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=matplotlib.colors.ListedColormap(cols),
    alpha=0.7,
    zorder=200,
    origin="lower",
    aspect="auto",
)


# Label with the date
ax.text(
    180 / args.zoom - (360 / args.zoom) * 0.009,
    90 / args.zoom - (180 / args.zoom) * 0.016,
    "%04d-%02d-%02d" % (args.year, args.month, args.day),
    horizontalalignment="right",
    verticalalignment="top",
    color="black",
    bbox=dict(
        facecolor=(0.6, 0.6, 0.6, 0.5), edgecolor="black", boxstyle="round", pad=0.5
    ),
    size=28,
    clip_on=True,
    zorder=500,
)


from get_data.SyCLoPS.SyCLoPS_load import (
    load_tracks,
    rotate_pole,
    interpolate_track,
    make_trail,
    last_date,
    first_date,
)

# Load the tracks for the date
tracks = load_tracks()
# Rotate the pole
tracks = rotate_pole(
    tracks, args.pole_longitude, args.pole_latitude, args.npg_longitude
)
# Reduce the tracks to the date
itracks = {}
itracks_before = {}
itracks_after = {}
for tid, track in tracks.items():
    last_dte = last_date(track) - datetime.timedelta(minutes=1)
    first_dte = first_date(track)
    itr = interpolate_track(track, dte)
    if itr is not None:
        itracks[tid] = itr
    else:
        if last_dte < dte and last_dte > dte - datetime.timedelta(hours=12):
            itr_b = interpolate_track(track, last_dte)
            itr_b["time_offset"] = dte - last_dte
            itracks_before[tid] = itr_b
        if first_dte > dte and first_dte < dte + datetime.timedelta(hours=12):
            itr_a = interpolate_track(track, first_dte)
            itr_a["time_offset"] = first_dte - dte
            itracks_after[tid] = itr_a


def pointsize(ws):  # Convert wind speed to point size
    return (np.sqrt(ws) / 5.0) * 2


def linewidth(ws):  # Convert wind speed to line width
    return (np.sqrt(ws) / 2.0) * 2


def plot_object(ax, track, tid, alpha=1):
    color = "red"
    ax.add_patch(
        matplotlib.patches.Circle(
            (track["LON"], track["LAT"]),
            radius=pointsize(track["WS"]),
            facecolor=color,
            edgecolor=color,
            linewidth=0.0,
            alpha=alpha,
            zorder=580,
        )
    )
    # Add the trails
    trail = make_trail(tracks, tid, dte)
    for i in range(len(trail) - 1):
        color = "red"
        if abs(trail[i]["LON"] - trail[i + 1]["LON"]) > 90:
            continue  # Skip lines that cross the 180th meridian
        ax.add_line(
            Line2D(
                [trail[i]["LON"], trail[i + 1]["LON"]],
                [trail[i]["LAT"], trail[i + 1]["LAT"]],
                linewidth=linewidth(trail[i]["WS"]),
                color=color,
                alpha=alpha * 0.5,
                zorder=550,
            )
        )


# Plot the objects
for tid, track in itracks.items():
    plot_object(ax, track, tid, alpha=1.0)

for tid, track in itracks_before.items():
    alpha = 1.0 - track["time_offset"].total_seconds() / 43200.0
    plot_object(ax, track, tid, alpha=alpha)
for tid, track in itracks_after.items():
    alpha = 1.0 - track["time_offset"].total_seconds() / 43200.0
    plot_object(ax, track, tid, alpha=alpha)


# Render the figure as a png
opfile = "%s/%04d%02d%02d%02d%02d.png" % (
    args.opdir,
    args.year,
    args.month,
    args.day,
    int(args.hour),
    int(args.hour % 1 * 60),
)
if args.debug:
    opfile = "debug.png"
fig.savefig(opfile)
