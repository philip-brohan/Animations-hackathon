# Load the cyclone tracks from Malcolm's dataset

tracks_file = (
    "/data/users/malcolm.roberts/SyCLoPS_REV/ERA5_SyCLoPS_classified_2020-21_subset.csv"
)
# Load the contents of the tracks file using the csv module
import csv
import datetime
import iris.analysis.cartography
import numpy as np


# Convert the list of lists into a list of dictionaries
# (assuming the first row contains the column names)
def load_tracks():
    with open(tracks_file, "r") as f:
        reader = csv.DictReader(f)
        # Read the rest of the rows into a list
        data = list(reader)
    # Convert the dates to datetime objects
    for row in data:
        row["datetime"] = datetime.datetime.strptime(
            row["ISOTIME"], "%Y-%m-%d %H:%M:%S"
        )
    # Convert numeric values to floats
    for row in data:
        for key in ("LON", "LAT", "MSLP", "WS", "Tropical_Flag", "Transition_Zone"):
            try:
                row[key] = float(row[key])
            except ValueError:
                pass
    # Mke sure the longitude is in the range -180 to 180
    for row in data:
        if row["LON"] > 180:
            row["LON"] -= 360
        elif row["LON"] < -180:
            row["LON"] += 360
    # Subset points by cyclone ID
    tracks_by_tid = {}
    for point in data:
        tid = point["TID"]  # Assuming 'TID' is the column name

        if tid not in tracks_by_tid:
            tracks_by_tid[tid] = []

        tracks_by_tid[tid].append(point)
    return tracks_by_tid


# Rotate the pole
def rotate_pole(tracks, pole_longitude, pole_latitude, npg_longitude):
    for tid, track in tracks.items():
        for point in track:
            rp = iris.analysis.cartography.rotate_pole(
                np.array(point["LON"]),
                np.array(point["LAT"]),
                pole_longitude,
                pole_latitude,
            )
            point["LON"] = rp[0][0] + npg_longitude
            if point["LON"] > 180:
                point["LON"] -= 360
            elif point["LON"] < -180:
                point["LON"] += 360
            point["LAT"] = rp[1][0]
    return tracks


# Interpolate a track to a given time
def interpolate_track(track, target_time):
    # Assuming track is a list of dictionaries with 'datetime' and other fields
    # Find the two points surrounding the target time
    before = None
    after = None

    for point in track:
        if point["datetime"] <= target_time:
            before = point
        elif point["datetime"] > target_time and after is None:
            after = point
            break

    if before is None or after is None:
        return None  # Cannot interpolate if we don't have both points

    # Interpolate the numeric values
    interpolated_point = {}
    for key in ("LON", "LAT", "MSLP", "WS", "Tropical_Flag", "Transition_Zone"):
        if key == "LON" and (after[key] - before[key]) > 180:
            after[key] -= 360
        if key == "LON" and (before[key] - after[key]) > 180:
            before[key] -= 360
        interpolated_point[key] = before[key] + (after[key] - before[key]) * (
            (target_time - before["datetime"]).total_seconds()
            / (after["datetime"] - before["datetime"]).total_seconds()
        )
        if key == "LON":
            if interpolated_point[key] > 180:
                interpolated_point[key] -= 360
            elif interpolated_point[key] < -180:
                interpolated_point[key] += 360

    interpolated_point["datetime"] = target_time
    return interpolated_point


# Make the trail of a cyclone
def make_trail(tracks, tid, target_time):
    track = tracks[tid]
    interpolated_track = []
    for point in track:
        if point["datetime"] <= target_time:
            interpolated_track.append(point)
        else:
            break
    return interpolated_track
