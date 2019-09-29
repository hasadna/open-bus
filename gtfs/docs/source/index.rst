Open-Bus GTFS Utils
===================

| GTFS Utils is a utility for reading, parsing and aggregating GTFS data from Israel MOT.
| GTFS Utils is part of `Open-Bus <https://github.com/hasadna/open-bus>`_ project in
  `The Public Knowledge Workshop ("הסדנה לידע ציבורי") <https://www.hasadna.org.il/>`_.

Usage
-----
To use GTFS Stats script, run:

.. code-block:: bash

    python setup.py install
    run_gtfs_stats

Configuration
-------------
| GTFS Utils requires a configuration file  ``config.json``.
| An example file can be found in ``gtfs_utils/config_example.json``.

bucket_valid_file_name_regexp
.............................
| Use ``bucket_valid_file_name_regexp`` field in configuration to choose which dates to run the script on.
| You can use a value such as ``"2019-03-07.zip"`` to run on a single date, or ``"2019-05-\d\d\.zip"`` to run on a full
  month, for example.

forward_fill
............
Set ``forward_fill`` field in configuration to ``true`` for performing forward fill for missing dates using existing
files.

Output format
-------------
| GTFS Stats outputs stats for trips and for routes (`trip_stats` and `route_stats`, accordingly).
| Each of them is output as a ``pkl.gz`` file (a gzipped `pickle <https://docs.python.org/3/library/pickle.html>`_) of a
  `Pandas DataFrame <http://pandas.pydata.org/pandas-docs/stable/reference/frame.html>`_, and is located in the
  ``output`` directory, as defined in the configuration file.
| The fields in each one of them are described in the output specifications below.

Output format as it is in Splunk
................................
*This section will be written soon.*

.. toctree::
   :caption: Output specifications

   trip_stats
   route_stats
