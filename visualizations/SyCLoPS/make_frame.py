#!/usr/bin/env python

# Make a single frame showing the SyCLoPS tracks

import os
import sys
import datetime

import iris
import iris.cube
import iris.analysis.cartography
import numpy as np

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

from get_data.SyCLoPS.SyCLoPS_load import (
    load_tracks,
    rotate_pole,
    interpolate_track,
    make_trail,
    last_date,
    first_date,
)
from get_data.ERA5_hourly.ERA5_hourly import get_land_mask

# Fix dask SPICE bug
import dask

dask.config.set(scheduler="single-threaded")

# Set colors
colors = {
    "HATHL": "red",
    "DOTHL": "green",
    "HAL": "blue",
    "TD(MD)": "black",
    "PL(PTLC)": "grey",
    "TLO": "green",
    "DST": "orange",
    "TC": "purple",
    "SC": "gold",
    "THL": "brown",
    "TD": "red",
    "DSE": "red",
    "TLO(ML)": "red",
    "DSD": "red",
    "EX": "red",
    "SS(STLC)": "red",
}

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
    default="%s/AnimH/visualizations/SyCLoPS" % os.getenv("SCRATCH"),
    type=str,
    required=False,
)
parser.add_argument(
    "--debug",
    help="Plot to debug image?",
    action="store_true",
    default=False,
    required=False,
)

args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)


dte = datetime.datetime(
    args.year, args.month, args.day, int(args.hour), int(args.hour % 1 * 60)
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


# Find tracks
mask = get_land_mask()

# Define the figure (page size, background color, resolution, ...
fig = Figure(
    figsize=(19.2 * 2, 10.8 * 2),  # Width, Height (inches)
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=True,
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


# Define an axes to contain the plot. In this case our axes covers
#  the whole figure
ax = fig.add_axes([0, 0, 1, 1])
ax.set_axis_off()  # Don't want surrounding x and y axis

# Lat and lon range (in rotated-pole coordinates) for plot
ax.set_xlim(-180 / args.zoom, 180 / args.zoom)
ax.set_ylim(-90 / args.zoom, 90 / args.zoom)
ax.set_aspect("auto")

# Background
ax.add_patch(
    Rectangle((-180, -90), 360, 180, facecolor=(0.9, 0.9, 0.9, 1), fill=True, zorder=1)
)

# Draw lines of latitude and longitude
for lat in range(-90, 95, 5):
    lwd = 0.25
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
    lwd = 0.25
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
mask_img = ax.imshow(
    mask.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=matplotlib.colors.ListedColormap(((0.8, 0.8, 0.8, 0), (0.8, 0.8, 0.8, 1))),
    vmin=0,
    vmax=1,
    alpha=1.0,
    zorder=20,
    origin="lower",
    aspect="auto",
)


def pointsize(ws):  # Convert wind speed to point size
    return (np.sqrt(ws) / 5.0) * 2


def linewidth(ws):  # Convert wind speed to line width
    return (np.sqrt(ws) / 2.0) * 2


def plot_object(ax, track, tid, alpha=1):
    #    color = (1.0 * track["Tropical_Flag"], 0, 1.0 - track["Tropical_Flag"], 1)
    try:
        color = colors[track["Short_Label"]]
    except KeyError:
        color = "black"
    ax.add_patch(
        matplotlib.patches.Circle(
            (track["LON"], track["LAT"]),
            radius=pointsize(track["WS"]),
            facecolor=color,
            edgecolor=color,
            linewidth=0.0,
            alpha=alpha,
            zorder=180,
        )
    )
    # Add the trails
    trail = make_trail(tracks, tid, dte)
    for i in range(len(trail) - 1):
        #        color = (1.0 * trail[i]["Tropical_Flag"], 0, 1.0 - trail[i]["Tropical_Flag"], 1)
        try:
            color = colors[trail[i]["Short_Label"]]
        except KeyError:
            color = "black"
        if abs(trail[i]["LON"] - trail[i + 1]["LON"]) > 90:
            continue  # Skip lines that cross the 180th meridian
        ax.add_line(
            Line2D(
                [trail[i]["LON"], trail[i + 1]["LON"]],
                [trail[i]["LAT"], trail[i + 1]["LAT"]],
                linewidth=linewidth(trail[i]["WS"]),
                color=color,
                alpha=alpha * 0.5,
                zorder=150,
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

# Render the figure as a png
fig.savefig(opfile)
