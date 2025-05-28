#!/usr/bin/env python

# Target and ML reconstructed precip fields

import os
from get_data.ML_tests.ML_data import load, get_land_mask
import datetime

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import cmocean

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
    "--opdir",
    help="Directory for output files",
    default="%s/AnimH/visualizations/ML_unet_mse" % os.getenv("SCRATCH"),
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


target = load("target", dte.year, dte.month, dte.day, dte.hour)
ml = load("unet-mse", dte.year, dte.month, dte.day, dte.hour)


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


# Define an axes to contain the background
ax = fig.add_axes([0, 0, 1, 1])
ax.set_axis_off()  # Don't want surrounding x and y axis
ax.add_patch(  # Background
    Rectangle((0, 0), 1, 1, facecolor=(0.9, 0.9, 0.9, 1), fill=True, zorder=1)
)

# Left hand axes for target
ax_target = fig.add_axes([0.01, 0.06, 0.485, 0.88])

# Lat and lon range (in rotated-pole coordinates) for plot
ax_target.set_aspect("auto")
ax_target.set_axis_off()
ax_target.add_patch(  # Background
    Rectangle((0, 0), 1, 1, facecolor=(0.95, 0.95, 0.95, 1), fill=True, zorder=10)
)

lats = mask.coord("grid_latitude").points
lons = mask.coord("grid_longitude").points
ax_target.imshow(
    mask.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=matplotlib.colors.ListedColormap(((0.4, 0.4, 0.4, 0), (0.4, 0.4, 0.4, 0.15))),
    vmin=0,
    vmax=1,
    alpha=1.0,
    zorder=200,
    origin="lower",
    aspect="auto",
)
ax_target.imshow(
    target.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=cmocean.cm.rain,
    vmin=0,
    vmax=50,
    alpha=1.0,
    zorder=20,
    origin="lower",
    aspect="auto",
)


# Right hand axes for ML output
ax_ML = fig.add_axes([0.505, 0.06, 0.485, 0.88])
ax_ML.set_aspect("auto")
ax_ML.set_axis_off()
ax_ML.add_patch(  # Background
    Rectangle((0, 0), 1, 1, facecolor=(0.95, 0.95, 0.95, 1), fill=True, zorder=10)
)
ax_ML.imshow(
    mask.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=matplotlib.colors.ListedColormap(((0.4, 0.4, 0.4, 0), (0.4, 0.4, 0.4, 0.15))),
    vmin=0,
    vmax=1,
    alpha=1.0,
    zorder=200,
    origin="lower",
    aspect="auto",
)
ax_ML.imshow(
    ml.data,
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    cmap=cmocean.cm.rain,
    vmin=0,
    vmax=50,
    alpha=1.0,
    zorder=20,
    origin="lower",
    aspect="auto",
)


# Label with the date
ax.text(
    0.985,
    0.97,
    "%04d-%02d-%02d" % (args.year, args.month, args.day),
    horizontalalignment="right",
    verticalalignment="top",
    color="black",
    bbox=dict(
        facecolor=(0.6, 0.6, 0.6, 0.5), edgecolor="black", boxstyle="round", pad=0.5
    ),
    size=48,
    clip_on=True,
    zorder=500,
)

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
