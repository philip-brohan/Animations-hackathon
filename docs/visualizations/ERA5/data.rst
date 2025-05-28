Assemble data for the ERA5 video
================================

We will download the data from the `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/>`_. This requires installing the `CDS API <https://cds.climate.copernicus.eu/how-to-api>`_ (:doc:`see the environment for this repository <../../how_to>`) and registering for an account on the CDS website.


Script to download one variable for one year:

.. literalinclude:: ../../../get_data/ERA5_hourly/get_year_of_hourlies.py

Run the script above repeatedly to get all the variables for the whole period. 

.. literalinclude:: ../../../get_data/ERA5_hourly/get_data_for_period_ERA5.py


As well as the weather data, the plot script needs a land-mask file to plot the continents. This script retrieves that.

.. literalinclude:: ../../../get_data/ERA5_hourly/get_land_mask.py


As well as downloading the data, we want some convenience functions to load it into a convenient format (`iris cubes <https://scitools-iris.readthedocs.io/en/latest/userguide/iris_cubes.html>`_). This script does that for the ERA5 data.:

.. literalinclude:: ../../../get_data/ERA5_hourly/ERA5_hourly.py
