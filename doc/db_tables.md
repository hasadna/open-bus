## Re:dash
You can query all our database tables using re:dash at http://data.obudget.org

Use your Google account to login.

## SIRI tables

Tables of data extracted from the SIRI service using [fetch_and_store_arrivals](https://github.com/hasadna/open-bus/blob/master/doc/fetch_and_store_arrivals.md). 

- `responses` - raw responses 
- `arrivals` - parsed response

## GTFS Tables

Tables loaded from the GTFS file. 
  * [More information about GTFS](https://github.com/hasadna/open-bus/blob/master/doc/working_with_GTFS.md) including an [Entity Relation Diagram](https://github.com/hasadna/open-bus/blob/master/doc/gtfs_src_entity_diagram.png). 
  * Examples of [GTFS-related SQL queries](https://github.com/hasadna/open-bus/blob/master/doc/useful_GTFS_queries.md)
  * Information about [inserting the GTFS to the DB](https://github.com/hasadna/open-bus/blob/master/doc/Inserting_GTFS_to_PostGRES.md).

- `agency`
- `routes`
- `stops`
- `trips`
- `calendar`
- `stop_times`
- `shape`

## Route Stories

Route stories are a compressed version of stop_times. See the [docstring of the module that generates them](https://github.com/hasadna/open-bus/blob/master/gtfs/parser/route_stories.py) for more info.

* `route_story_stops`
* `trip_route_stories` 

## Bus stops near train stations

Data generated for the bus2train task.  See [issue #7](https://github.com/hasadna/open-bus/issues/7) for more information on how and why they were created. 

- `train_station_exits` has coordinates of the entrances and exits to train stations (the GTFS stops table only have an approximate coordinate in the middle of each station). 

- `station_walking_distance` has bus stops that are near train stations. Each line gives one possible distance between a bus stop and a station. Stop & station are identified by the stop code. `Source` field specify how the distance was retrieved. Current values: Google for Google Maps Routing API, Graphopper for [Graphopper Routing API](https://graphhopper.com/). 'Estimation' will mean distance estimated manually where routing isn't available. 


## Train passengers counts

  `train_passenger_counts`
  
The number of passengers traveling beween each pair of train stations, per month.

We currenly have data for January - April 2016. This data was originally published in Tapuz's Public Transport forum. It seems that it arrives from Israel Railway spokesperson's office, but it's not clear how it was calculated by Isral Railway. The originl file from the forum is [here](https://github.com/daphshez/openbus_data/blob/master/train_station_passengers/passenger%20by%20line%202016-01-04.xlsx). 

Open train project have [an archive of older data published in the same forum](http://otrain.org/files/count/). There are per-station statistics rather than per station pair. 


