The files in this directory are meant to be used to test the output of gtfs_stats and route_stats.
The input files (in inputs/ directory) were created by
taking the actual gtfs file (israel-public-transportation.zip) and Tariff.zip file and filtering them so that
only rows that match routes with ID 1, 2 or 3 were left.
The output files (outputs/2019-03-07_route_stats.pkl.gz and outputs/2019-03-07_trip_stats.pkl.gz) were created by
running gtfs_stats script on the input files described above, before the refactor (https://github.com/hasadna/open-bus/issues/161).
The output should remain the same, to fit the original format.
