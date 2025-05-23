#!/usr/bin/env python

# Make all the individual frames for a movie

import os
import cftime
import datetime


# Function to check if the job is already done for this timepoint
def is_done(year, month, day, hour):
    op_file_name = (
        "%s/AnimH/visualizations/ML_diffusion/" + "%04d%02d%02d%02d%02d.png"
    ) % (
        os.getenv("SCRATCH"),
        year,
        month,
        day,
        int(hour),
        int(hour % 1 * 60),
    )
    if os.path.isfile(op_file_name):
        return True
    return False


f = open("run.txt", "w+")

start_day = cftime.datetime(1981, 3, 1, 12, calendar="360_day")
end_day = cftime.datetime(1981, 5, 30, 12, calendar="360_day")

current_day = start_day
while current_day <= end_day:
    if is_done(
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour + current_day.minute / 60,
    ):
        current_day = current_day + datetime.timedelta(hours=1)
        continue
    cmd = ("./make_frame.py --year=%d --month=%d " + "--day=%d --hour=%d " + "\n") % (
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour,
    )
    f.write(cmd)
    current_day = current_day + datetime.timedelta(hours=1)
f.close()
