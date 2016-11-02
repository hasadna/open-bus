# Distance between bus stops and train stations

To deal with transfers between buses and train (e.g. for bus2train task), we need to know which bus stops are near train stations.

### Straight line distance

We started with a naive approach of straight line between the bus stop coordinate and the train station coordinate in the GTFS stops table (or file). The script that does that is `gtfs.parser.nearest_station`. It's recommended to run this script after loading the GTFS to db.  It adds two two fields to the stops table (if they don't exist already): `TRAIN_STATION_DISTANCE` (in meters) and `NEAREST_TRAIN_STATION` (which is the stop id of the train station).

### Walking distance

As you would expect, the walking distance in many cases can be much longer than the direct line distance. After a lot of trial and error ([documented here](https://github.com/hasadna/open-bus/issues/7)), it seems that the best approach is:

1. Find coordinates for the actual entrances and exits from train stations. This is a manual process that was done using Google Street View, govmap.gov.il aerial photos, & local knowledge (we posted questions on forums). The result of this effort is in the `train_station_exits` table and also in [this file](https://github.com/daphshez/openbus_data/blob/master/train_stations/train_station_exits.csv). 
2. Run routing queries between stops and stations, for stops that are close enough to stations. Run queries on both Google Maps API and Graphopper API. These two services use different map data (Google Maps uses GIsrael, Graphopper uses OSM) and different algorithms, and give different results. The script that does that is at `gtfs.bus2train.walking_distance`. Running the script requires API keys for the two services (they are free to get). Note that Graphhopper only allows for 300 requests a day. The results of this query are currently in the `station_walking_distance` table. 
3. Make some choice between the two numbers (average? minimum?) depending on the use. 