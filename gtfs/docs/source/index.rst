Open-Bus GTFS Utils
===================

| GTFS Utils is a utility for reading, parsing and aggregating GTFS data from Israel MOT.
| GTFS Utils is part of `Open-Bus <https://github.com/hasadna/open-bus>`_ project in
  `The Public Knowledge Workshop ("הסדנה לידע ציבורי") <https://www.hasadna.org.il/>`_.

Usage
-----
To use GTFS Stats script, run:

.. code-block:: bash

    python gtfs_utils/gtfs_stats.py

Configuration
-------------
| GTFS Utils requires a configuration file  ``config.json``.
| An example file can be found in ``gtfs_utils/config_example.json``.

Output format
-------------
| GTFS Stats outputs stats for trips and for routes (`trip_stats` and `route_stats`, accordingly).
| Each of them is output as a ``pkl.gz`` file (a gzipped `pickle <https://docs.python.org/3/library/pickle.html>`_) of a
  `Pandas DataFrame <http://pandas.pydata.org/pandas-docs/stable/reference/frame.html>`_, and is located in the
  ``output`` directory, as defined in the configuration file.
| The fields in each one of them are described in the output specifications below.

.. toctree::
   :caption: Output specifications

   trip_stats
   route_stats
