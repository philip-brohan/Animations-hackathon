Downscaling: 3-hourly data
==========================

.. raw:: html

    <center>
    <table><tr><td><center>
    <iframe src="https://player.vimeo.com/video/1087981124?title=0&byline=0&portrait=0" width="795" height="448" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></center></td></tr>
    <tr><td><center>3-hourly precipitation (from a physical model).</center></td></tr>
    </table>
    </center>

This video shows England and Wales precipitation, taken at 3-hourly intervals from a high-resolution physical model. 

To make a video, the 3-hourly values are interpolated to 15-minute values, and then the 15-minute values are shown as a sequence of frames. This does not work brilliantly, as weather features can move far enough in 3 hours that the interpolation does not capture the features well - we can see 3-hourly artifacts in the video - we really need hourly data (or more frequent) to make a good video of precipitation at this space scale. But sometimes we have to work with what we have.

Data source is the same as that used in the :doc:`diffusion model <../Downscaling_diffusion/index>` example.
  
.. toctree::
   :titlesonly:
   :maxdepth: 1

   Plot a single frame <plot>
   Plot all the frames and make a video <video>
    


