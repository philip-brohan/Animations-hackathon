Downscaling: Diffusion model
============================


.. raw:: html

    <center>
    <table><tr><td><center>
    <iframe src="https://player.vimeo.com/video/1087980537?title=0&byline=0&portrait=0" width="795" height="448" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></center></td></tr>
    <tr><td><center>Left: target precipitation (from a physical model). Right: Estimate from an ML diffusion model</center></td></tr>
    </table>
    </center>

This video shows two versions of the same precipitation field, one from a physical model (left) and one from a machine-learning diffusion model trained on the physical model outputs (right). The aim is to judge the quality of the diffusion model - how well does it reproduce the physical model results.

The precipitation field is a sequence of daily averages. For the physical model that's a daily average of high-frequency model output - the diffusion model calculates daily averages directly. To make a video, the daily averages are interpolated to hourly values, and then the hourly values are plotted as a sequence of frames.
 

  
.. toctree::
   :titlesonly:
   :maxdepth: 1

   Get the data <data>
   Plot a single frame <plot>
   Plot all the frames and make a video <video>
    


