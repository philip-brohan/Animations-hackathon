ERA5 in video
=============


.. raw:: html

    <center>
    <table><tr><td><center>
    <iframe src="https://player.vimeo.com/video/1087973371?title=0&byline=0&portrait=0" width="795" height="448" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></center></td></tr>
    <tr><td><center>Near-surface temperature, wind, and precipitation. From the ERA5 Reanalysis</center></td></tr>
    </table>
    </center>

This video shows near-surface weather, as reconstructed by `ERA5 <https://confluence.ecmwf.int/display/CKB/ERA5>`_. (I've made very similar visualizations before, for both `The Met Office operational analysis <https://brohan.org/ML_GCM/visualisation/MO_global_analysis/index.html>`_ and `the 20th Century Reanalysis <https://oldweather.github.io/20CRv3-diagnostics/fog_videos/1931.html>`_.)

  
.. toctree::
   :titlesonly:
   :maxdepth: 1

   Get the data <data>
   Plot a single frame <plot>
   Plot all the frames and make a video <video>
    

ERA5 is easily available as hourly data, making it a great choice for videos like this, as one frame an hour is enough to make a smooth video, so it's not even necessary to interpolate in time. But there is a catch - the reanalysis is run with an assimilation step every 12 hours, and the next 11 hours are forecast from that step, and then there is a discontinuity to the next assimilation state. For the assimilated variables (temperature and wind) this doesn't matter, but for precipitation it does, and you can see the discontinuity in tropical precip. every 12 hours (0.5s elapsed) in the video. But it's a small effect, and it's a right pain to do anything about it, so I left it in.

