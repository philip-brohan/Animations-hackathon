Make all the frames and combine into a video
============================================

To make the video we need to run the :doc:`plot script <plot>` thousands of times, making an image file for each point in time, and then to merge the thousands of resulting images into a single video.

To make a smooth video we generate one frame every hour.

This script calls the :doc:`plot script <plot>` for each hour over a period:

.. literalinclude:: ../../../visualizations/SyCLoPS/make_all_frames.py

We then run those jobs in parallel, either with `GNU parallel <https://www.gnu.org/software/parallel/>`_ or by submitting them to a batch system (I used the MO SPICE cluster).

When all the frame images are rendered we make a video using `ffmpeg <https://www.ffmpeg.org/>`_. We will render at 1080p resolution - 5Mb/s bandwidth. (Overkill for a simple video, but now everyone has lots of internet bandwidth, so it's not worth optimizing).

.. literalinclude:: ../../../visualizations/SyCLoPS/ffmpeg.sh
