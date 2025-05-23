#!/usr/bin/env python

# Make all the individual frames for a movie

import os
import cftime
import datetime


# Function to check if the job is already done for this timepoint
def is_done(year, month, day, hour, minute):
    op_file_name = (
        "%s/AnimH/visualizations/3_hr_precip/" + "%04d%02d%02d%02d%02d.png"
    ) % (
        os.getenv("SCRATCH"),
        year,
        month,
        day,
        hour,
        minute,
    )
    if os.path.isfile(op_file_name):
        return True
    return False


f = open("run.txt", "w+")

start_day = cftime.datetime(2021, 1, 1, 0, calendar="360_day")
end_day = cftime.datetime(2021, 12, 30, 18, calendar="360_day")

current_day = start_day
while current_day <= end_day:
    if is_done(
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour,
        current_day.minute,
    ):
        current_day = current_day + datetime.timedelta(minutes=15)
        continue
    cmd = (
        "./make_frame.py --year=%d --month=%d "
        + "--day=%d --hour=%d --minute=%d"
        + "\n"
    ) % (
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour,
        current_day.minute,
    )
    f.write(cmd)
    current_day = current_day + datetime.timedelta(minutes=15)
f.close()
