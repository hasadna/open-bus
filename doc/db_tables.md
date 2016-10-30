## SIRI tables

Tables of data extracted from the SIRI service using [fetch_and_store_arrivals](https://github.com/hasadna/open-bus/blob/master/doc/fetch_and_store_arrivals.md). 

- `responses` - raw responses 
- `arrivals` - parsed response

## GTFS Tables

Tables loaded from the GTFS file. [More information about GTFS](https://github.com/hasadna/open-bus/blob/master/doc/working_with_GTFS.md) including an [Entity Relation Diagram](https://github.com/hasadna/open-bus/blob/master/doc/gtfs_src_entity_diagram.png). Information about [inserting the GTFS to the DB](https://github.com/hasadna/open-bus/blob/master/doc/Inserting_GTFS_to_PostGRES.md).

- `agency`
- `routes`
- `stops`
- `trips`
- `calendar`
- `stop_times`
- `shape`

## Route Stories

Route stories are a compressed version of stop_times. See the d[ocstring of the module that generates them](https://github.com/hasadna/open-bus/blob/master/gtfs/parser/route_stories.py) for more info.

* `route_story_stops`
* `trip_route_stories` 

## Bus stops near train stations

Data generated for the bus2train task.  See [issue #7](https://github.com/hasadna/open-bus/issues/7) for more information on how and why they were created. 

- `train_station_exits` has coordinates of the entrances and exits to train stations (the GTFS stops table only have an approximate coordinate in the middle of each station). 

- `station_walking_distance` has bus stops that are near train stations. It includes the straight line distance, and the length of the walking route using two route services: Google Maps and [Graphopper](https://graphhopper.com/). 

  ​
