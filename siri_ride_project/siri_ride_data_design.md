# SiriRide class - data design (version 1.0)

Design for variables to be calculated for each SiriRide instance.

Variables have separated into different categories by 2 criteria: Data needed and Data Science work needed.

## Data Categories
Category | Data needed | DS work needed 
-- | -- | -- 
0 | SiriRide only | raw data only
1 | SiriRide only | straightforward calculations
2 | SiriRide only  | complex calculations - statistics/modeling 
3 | SiriRide and GTFS route stats | straightforward calculations
4 | SiriRide and GTFS route stats | complex calculations - statistics/modeling

More categories will be added in the next versions (e.g. when we will need to use aggregated  SiriRide's data for comparing one SiriRide to other "similar"/historical rides, or to use GTFS shape files). 

## Variables

Category | Variable | Source name | Desc | Dependencies | Dtype | Comments
-- | -- | -- | -- | -- | -- | --
0 | agency_id | OperatorRef - siri (agency_id in gtfs, operatorRef in SiriLogV2) | | **siri raw data** | int | SiriRide index    
0 | route_id | LineRef - siri (route_id in gtfs, lineRef in SiriLogV2) | | **siri raw data** | int | SiriRide index    
0 | route_short_name | PublishedLineName - siri (route_short_name in gtfs, lineName in SiriLogV2) | | **siri raw data** | int | **to verify it's always int**   
0 | bus_id | VehicleRef - siri (licensePlate in SiriLogV2) | | **siri raw data** | int | SiriRide index    
0 | planned_start_date | date from OriginAimedDepartureTime - siri (departure_time in gtfs, departureTime in SiriLogV2) | | **siri raw data** | date | SiriRide index  
0 | planned_start_datetime | OriginAimedDepartureTime in siri (departure_time in gtfs, departureTime in SiriLogV2) | | **siri raw data** | datetime | SiriRide index 
1 | service_ids | DatedVehicleJourneyRef - siri (TripId in gtfs - 'TripIdToDate.txt', journryRef in SiriLogV2) | list of unique service_id in SiriRide | **siri raw data** | list of int | mostly will be only one value in the list
1 | pts_timestamps | responseTimestamp - SiriLogV2 | list of points timestamps by create timestamp | **siri raw data** | list of datetime 
1 | pts_times | RecordedAtTime - siri (recordedAt in SiriLogV2) | list of points timestamps by time_recorded (ordered by create timestamp) | **siri raw data** | list of datetime 
1 | pts_latlons | Longitude & Latitude - siri (lon & lat in SiriLogV2) | list of points latlon's (ordered by create timestamp) | **siri raw data** | list of tuples of floats 
1 | num_pts | | number of geo points in SiriRide | pts_times | int 
1 | first_record | | timestamp of first record | pts_times | datetime  
1 | last_record | | timestamp of last record | pts_times | datetime
1 | first_actual_record | | timestamp of first record that had actual lat,lon (not 0.0,0.0) | pts_times, pts_latlons | datetime  
1 | last_actual_record | | timestamp of last record that had actual lat,lon (not 0.0,0.0) | pts_times, pts_latlons | datetime 
1 | total_ride_time_minutes | | time (minutes) from first non 0 time point until the last one | first_actual_record, last_actual_record | float
1 | total_ride_distance_km | | distance (km) from first non 0 time point until the last one | pts_times, pts_latlons | float
1 | max_time_bwn_pts_seconds | | max time (seconds) between two adjacent points | pts_times | float 
2 | is_loop | | indication if the bus go back and forth or loop | pts_times, pts_latlons | boolean 
3 | ride_in_gtfs | | specific ride is listed in the gtfs (agency_id + route_id + planned_start_date + planned_start_time) | **route_stats** | boolean
3 | ride_date_in_gtfs | | ride date is listed in the gtfs (agency_id + route_id + planned_start_date) | **route_stats** | boolean  
3 | ride_route_in_gtfs | | ride route is listed in the gtfs (agency_id + route_id) | **route_stats** | boolean 
3 | ride_agency_in_gtfs | | ride agency is listed in the gtfs (agency_id) | **route_stats** | boolean
3 | planned_start_datetime_gtfs | | ride planned start time (as timestamp) by gtfs - if ride_in_gtfs = 1 then equal to planned_start_datetime, if only ride_date_in_gtfs = 1 then takes from gtfs the planned_start_datetime which is adjacent and before planned_start_datetime from siri | **route_stats**, ride_in_gtfs, ride_date_in_gtfs = 1 | datetime
3 | planned_end_datetime_gtfs | | ride planned end time (as timestamp) by gtfs (use the ride of planned_start_datetime_gtfs when ride_in_gtfs = 0) | **route_stats**, planned_start_datetime_gtfs, ride_in_gtfs, ride_date_in_gtfs = 1 | datetime 
3 | planned_driving_time_minutes | | ride planned driving time (minutes) | planned_start_datetime_gtfs, planned_end_datetime_gtfs | float 
3 | stops_ids | stop_id - gtfs | list of stops id's by gtfs | **route_stats**, ride_date_in_gtfs = 1 | list of int
3 | stops_latlons | stop_lat & stop_lon - gtfs | list of stops latlon's by gtfs | **route_stats**, ride_date_in_gtfs = 1 | list of tuples of floats 
3 | start_stop_city | substring from stop_desc - gtfs | start stop city by gtfs | **route_stats**, ride_date_in_gtfs = 1 | string
3 | end_stop_city | substring from stop_desc - gtfs | end stop city by gtfs | **route_stats**, ride_date_in_gtfs = 1 | string
3 | num_stops | | number of stops in route_id by gtfs | stops_ids, ride_date_in_gtfs = 1 | int
3 | stops2siri_best_distances | | list of distances (meters) between each stop and its nearest siri point | pts_latlons, stops_latlons, ride_date_in_gtfs = 1 | list of floats
3 | matching_by_stops_pct_500m | | percentage of stops with nearest siri point in distance of 500m | stops_best_distances, ride_date_in_gtfs = 1 | float
3 | matching_by_stops_pct_1000m | | percentage of stops with nearest siri point in distance of 1000m | stops_best_distances, ride_date_in_gtfs = 1 | float
4 | matching_by_stops_label | | labels for ride completion level by stops matching calculations - complete, missing (start / end / mid / other) | stops_best_distances, matching_by_stops_pct_500m, matching_by_stops_pct_1000m | string | **rules will be defined**    
4 | is_valid_ride | | indication if the ride data is valid for high-level calculations | matching_by_stops_label, is_loop, max_time_gap_bwn_pts, num_pts, ?? | boolean |**rules will be defined (may include filtering by agency_id)**   
4 | start_datetime_est | | estimated departure time from first station (as timestamp) | pts_times, pts_latlons, stops_latlons, is_valid_ride = 1 | datetime
4 | is_late_departure | | indication if the bus departed from the first stop after the scheduled time | start_datetime_est, planned_start_datetime_gtfs, is_valid_ride = 1 | boolean |**rules will be defined** 
4 | is_early_departure | | indication if the bus departed from the first stop before the scheduled time | start_datetime_est, planned_start_datetime_gtfs, is_valid_ride = 1 | boolean |**rules will be defined** 
4 | end_datetime_est | | estimated arrival time to last station (as timestamp) | pts_times, pts_latlons, stops_latlons, is_valid_ride = 1 | datetime 
4 | stops_times_est | | list of estimated stops times (as timestamps) | pts_times, pts_latlons, stops_latlons, start_datetime_est, end_datetime_est, is_valid_ride = 1 | list of datetime 
4 | driving_time_est_minutes | | estimated driving time (minutes) from first station to last station | start_datetime_est, end_datetime_est, is_valid_ride = 1 | float
4 | driving_distance_est_km | | estimated driving distance (km) from first station to last station | start_datetime_est, end_datetime_est, stops_latlons, pts_times, pts_latlons, is_valid_ride = 1 | float 
4 | driving_speed_est_kmh | | estimated driving speed (kmh) from first station to last station | driving_time_est_minutes, driving_distance_est_km, is_valid_ride = 1 | float


