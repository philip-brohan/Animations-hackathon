#!/bin/bash

cd $SCRATCH/AnimH/visualizations/
ffmpeg -r 36 -pattern_type glob -i 3_hr_precip/\*.png \
       -c:v libx264 -threads 16 -preset veryslow -tune film \
       -profile:v high -level 4.2 -pix_fmt yuv420p \
       -b:v 5M -maxrate 5M -bufsize 20M \
       -c:a copy 3_hr_precip.mp4
