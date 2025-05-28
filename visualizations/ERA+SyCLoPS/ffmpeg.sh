#!/bin/bash

cd $SCRATCH/AnimH/visualizations/
ffmpeg -r 24 -pattern_type glob -i ERA+SYCLoPS/\*.png \
       -c:v libx264 -threads 16 -preset veryslow -tune film \
       -profile:v high -level 4.2 -pix_fmt yuv420p \
       -b:v 19M -maxrate 19M -bufsize 20M \
       -c:a copy ERA+SYCLoPS.mp4
