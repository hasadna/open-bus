We have a service for polling the SIRI service for real-time bus data and aggregating it in the database. The data is parsed and saved into siri_arrivals table.

This document is meant to describe the important fields in that table and what we know about them. The full documentation of the SIRI protocol [is here](https://github.com/hasadna/open-bus/blob/master/doc/working_with_SIRI.md). 

The most interesting fields: 

* RECORDED_AT_TIME - time stamp as record by SIRI. 
* LINE_REF- bus line id (this is actually line number, direction and alternative). Should match the route_id in the gtfs_routes table.
* VEHICLE_REF - an identifier of the physical vehicle doing the trip. Often vehicle registration number (license plate), but in Dan it's an internal number called "machine number".
* ORIGIN_AIMED_DEPARTURE_TIME - the time when this bus should have left it's origin station. This could be used to match this trip to the planned trips tables.
* VEHICLE_LOCATION_LAT, VEHICLE_LOCATION_LON - the current position of the vehicle at time  RECORDED_AT_TIME.

Other fields that may have value: 

* MONITORING_REF - stop code. Each SIRI request is sent for a specific stop (rather than for example for a bus line), so each reply should have a stop code. The stop code should match the stop_code field in the gtfs_stops table.
* PUBLISHED_LINE_NAME - the line number as it is known to the public (appears on the bus & stop signs)
* OPERATOR_REF - code for the agency operating the line. Should match agency_id field in gtfs_agencies table.
* DESTINATION_REF - stop code of the terminal station of the line. 
* VEHICLE_AT_STOP - boolean, is the bus in the stop when at this time (which stop? see monitoring ref)
* EXPECTED_ARRIVAL_TIME - an estimation of the time the vehicle will arrive to the stop. This is what is often presented in apps like Moovit and on signs in the stops. The forecast quality is low.