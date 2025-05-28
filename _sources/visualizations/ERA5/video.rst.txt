Make all the frames and combine into a video
============================================

To make the video we need to run the :doc:`plot script <plot>` thousands of times, making an image file for each point in time, and then to merge the thousands of resulting images into a single video.

To make a smooth video we generate one frame every hour.

This script calls the :doc:`plot script <plot>` for each hour over a period:

.. literalinclude:: ../../../visualizations/ERA5/make_all_frames.py

We then run those jobs in parallel, either with `GNU parallel <https://www.gnu.org/software/parallel/>`_ or by submitting them to a batch system (I used the MO SPICE cluster).

When all the frame images are rendered we make a video using `ffmpeg <https://www.ffmpeg.org/>`_. Because of all the detail in the wind and precipitation fields, this video requires a lot of bandwidth, so render it at 20Mbps bandwidth (this is also why the frames are 3840X2160 in size - this produces a 4k video).

.. literalinclude:: ../../../visualizations/ERA5/ffmpeg.sh