## Re:dash
You can query all our database tables using re:dash at app.redash.io/hasadna

Use your Google account to login.

## SIRI tables

Tables of data extracted from the SIRI service using [fetch_and_store_arrivals](https://github.com/hasadna/open-bus/blob/master/doc/fetch_and_store_arrivals.md). See `working_with_SIRI.md` for more information about the SIRI protocol. 

- `siri_raw_responses` - raw responses xml

- `siri_arrivals` - parsed response

### SIRI arrivals

This table shows how the fields in the database relate to the SIRI response fields. See `working_with_SIRI.md` for more information about the SIRI response fields. 

| Database                      | SIRI                                     | Description                              |
| ----------------------------- | ---------------------------------------- | ---------------------------------------- |
| `id`                          | -                                        | database auto increment identifier       |
| `recorded_at_time`            | `MonitoredStopVisit.RecordedAtTime`      | time stamp                               |
| `item_identifier`             | `MonitoredStopVisit.ItemIdentifier`      | ?                                        |
| `monitoring_ref`              | `MonitoredStopVisit.MonitoringRef`       | ?                                        |
| `line_ref`                    | `MonitoredVehicleJourney.LineRef`        | GTFS route code                          |
| `direction_ref`               | `MonitoredVehicleJourney.DirectionRef`   | probably direction from GTFS routes table (values are 1, 2 or 3) |
| `operator_ref`                | `MonitoredVehicleJourney.OperatorRef`    | GTFS agency id                           |
| `published_line_name`         | `MonitoredVehicleJourney.PublishedLineName` | Line number as it appears to the public (e.g. on the bus) |
| `destination_ref`             | `MonitoredVehicleJourney.DestinationRef` | GTFS stop code of the destination (last stop) |
| `dated_vehicle_journey_ref`   | `MonitoredVehicleJourney.DatedVehicleJourneyRef` | **should be** the GTFS trip id, in practice always empty |
| `vehicle_ref`                 | `MonitoredVehicleJourney.VehicleRef`     | Vehicle identifier, usually vehicle registration number (but in Dan an internal "machine number") |
| `confidence_level`            | `MonitoredVehicleJourney.ConfidenceLevel` | always empty                             |
| `origin_aimed_departure_time` | `MonitoredVehicleJourney.OriginAimedDepartureTime` | **probably** the planned departure time from the first stop. If true, could be matched to find the trip in the GTFS. |
| `stop_point_ref`              | `MonitoredCall.StopPointRef`             | Stop code for which the rest of the Monitor Call information applies. |
| `vehicle_at_stop`             | `MonitoredCall.VehicleAtStop`            | Boolean field - is the bus currently in the stop. |
| `request_stop`                | `MonitoredCall.RequestStop`              | always false                             |
| `destination_display`         | `MonitoredCall.DestinationDisplay`       | always empty                             |
| `aimed_arrival_time`          | `MonitoredCall.AimedArrivalTime`         | Planned arrival time to stop (according to GTFS?) |
| `actual_arrival_time`         | `MonitoredCall.ActualArrivalTime`        | always empty                             |
| `expected_arrival_time`       | `MonitoredCall.ExpectedArrivalTime`      | Current estimated arrival time to stop (time to be displayed on signs / apps) |
| `arrival_status`              | `MonitoredCall.ArrivalStatus`            | delayed, onTime or empty                 |
| `arrival_platform_name`       | `MonitoredCall.ArrivalPlatformName`      | always empty                             |
| `arrival_boarding_activity`   | `MonitoredCall.ArrivalBoardingActivity`  | always empty                             |
| `actual_departure_time`       | `MonitoredCall.ActualDepartureTime`      | always empty                             |
| `aimed_departure_time`        | `MonitoredCall.AimedDepartureTime`       | always empty                             |
| `stop_visit_note`             | `MonitoredVehicleJourney.StopVisitNote`  | always empty                             |
| `response_id`                 | -                                        | Foreign key for matching raw in SIRI_raw_responses |
| `vehicle_location_lat`        | `MonitoredVehicleJourney.VehicleLocation.Latitude` | Location of the vehicle                  |
| `vehicle_location_lon`        | `MonitoredVehicleJourney.VehicleLocation.Longitude` | Location of the vehicle                  |
| `trip_id_from_gtfs`           | -                                        | trip id matched by `adding_trip_id_to_siri_from_gtfs.sql`|
| `route_offset`                | -                                        |  the location of the vechile comparing to the route in percentage. |

### SIRI Real Time Arrivales

Table created by (add here). The table contains the estimated arrival time by trip id based on the siri arrivals table.

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

  `train passengers per hour`

The number of passengers arriving \ leaving a station, per:

- Station (station_code, get full station data from stops table)
- Date
- Hour 

Data currently available for April-November 2016, received from Israel Railways using a FOI request. Raw Excel file as received from IR [here]([https://drive.google.com/drive/u/0/folders/0B9FEqRIWfmxLZllpdzlndVh2TVE](https://drive.google.com/drive/u/0/folders/0B9FEqRIWfmxLZllpdzlndVh2TVE)), csv extracted from Excel [here](https://drive.google.com/open?id=0B9FEqRIWfmxLMDl4VnBKcU1Qd0E). 

Currently only data for passengers *leaving* stations was loaded into DB (hence leaving=true for all records). 

`train_passenger_counts`

The number of passengers traveling beween each pair of train stations, per month. We currenly have data for January - April 2016. This data was originally published in Tapuz's Public Transport forum. It seems that it arrives from Israel Railway spokesperson's office, but it's not clear how it was calculated by Isral Railway. The originl file from the forum is [here](https://github.com/daphshez/openbus_data/blob/master/train_station_passengers/passenger%20by%20line%202016-01-04.xlsx).  Open train project have [an archive of older data published in the same forum](http://otrain.org/files/count/). There are per-station statistics rather than per station pair. 


