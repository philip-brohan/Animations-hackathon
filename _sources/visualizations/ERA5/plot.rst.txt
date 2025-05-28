Plot one frame from the ERA5 video
==================================

The video shows temperature, wind, and precipitation. Getting three variables into one image requires some care in presentation, particularly in the choice of colours used.

* The temperature is a colour map. It is quantile normalized - that is, the temperature field is scaled so that its distribution is flat - this means that the image shows the same amount of each colour. Also, the temperatures are adjusted to enhance the weather variability, and suppress the climatological variability and the diurnal cycle (the temperature anomalies are doubled, and the diurnal cycle reduced to 1/4 of its real size). This allows diurnal variability, the annual cycle, fixed effects like orography and the Gulf Stream, and weather-timescale variability, all to be shown in the same plot, without any one component dominating.
* Precipitation is only shown where it exceeds a threshold value (very light precipitation is missing). It is plotted on a log scale, using the 'algae' colour scale from `cmocean <https://matplotlib.org/cmocean/>`_, adjusted to taper to transparency at the bottom end.
* Wind is shown as advected speckles - a random field advected along with the wind vectors - this turns the speckles into stripes in the direction of the wind. They can be made to move from frame to frame by advecting most them a little more each time-step (and resetting a few of them to zero advection). This is plotted by adding the wind field to the temperature and precipitation fields before plotting them. The field has mean zero, so it has no average effect, but it perturbs the other fields in a way which shows the wind structure.

Script to make a single frame:

.. literalinclude:: ../../../visualizations/ERA5/make_frame.py

The script requires a pre-calculated (and saved) noise field (the speckles for the wind). This has to be pre-calculated as it needs to be the same for all frames:

.. literalinclude:: ../../../visualizations/ERA5/make_noise_field.py

For the functions to load the data, see the :doc:`get-data page <data>`.