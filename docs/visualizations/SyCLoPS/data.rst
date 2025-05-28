Assemble data for the SyCLoPS video
===================================

I got the data from `Malcolm Roberts <https://www.metoffice.gov.uk/research/people/malcolm-roberts>`_. I'm not including it here, but it comes as a CSV file like this:

.. code-block:: csv

    ,TID,LON,LAT,ISOTIME,MSLP,WS,Full_Name,Short_Label,Tropical_Flag,Transition_Zone,Track_Info,LPSAREA,IKE
    7259781,353897,30.25,8.0,2020-02-01 00:00:00,100961.4,4.639237,Thermal Low,THL,1.0,0.0,Track,0,0.0
    7259782,353897,30.0,7.0,2020-02-01 03:00:00,101083.2,4.169771,Thermal Low,THL,1.0,0.0,Track,0,0.0
    ...


So it's straightforward to write a function to load into a python dictionary. Because we're making a video, each frame will need to plot a point in time, and we'll need a higher time-frequency for frames than the SyCLoPS data provides. So we add an ```interpolate_track``` function to get an event at an arbitrary time.

.. literalinclude:: ../../../get_data/SyCLoPS/SyCLoPS_load.py