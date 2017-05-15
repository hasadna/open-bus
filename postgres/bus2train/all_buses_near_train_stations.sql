/* create walking distance table with train station name and min walking distance */
 WITH walking_with_station_name
     AS (SELECT station_walking_distance.bus_stop_code,
                station_walking_distance.train_station_code,
                Min(station_walking_distance.distance_in_meters) AS
                walking_distance,
                gtfs_stops.stop_name
         FROM   station_walking_distance
                join gtfs_stops
                  ON station_walking_distance.train_station_code =
                     gtfs_stops.stop_code
         GROUP  BY bus_stop_code,
                   train_station_code,
                   stop_name)

/* extract all bus times near train station */
SELECT DISTINCT
       walking_with_station_name.train_station_code           AS train_stop,
       walking_with_station_name.stop_name                    AS train_stop_name,
       gtfs_stops.stop_name                                        AS bus_stop_name,
       Date_part('hour', gtfs_stop_times.arrival_time :: interval) AS hour,
       gtfs_stop_times.arrival_time                              AS bus_time,
       gtfs_routes.route_short_name                                AS bus_route,
       gtfs_calendar.sunday                                        AS bus_sunday,
       gtfs_calendar.monday                                        AS bus_monday,
       gtfs_calendar.tuesday                                       AS bus_tuesday,
       gtfs_calendar.wednesday                                     AS bus_wednesday,
       gtfs_calendar.thursday                                      AS bus_thursday,
       gtfs_calendar.friday                                        AS bus_friday,
       gtfs_calendar.saturday                                      AS bus_saturday,
       gtfs_routes.route_desc                                      AS bus_route_makat,
      gtfs_calendar.start_date                                    AS start_date,
       gtfs_calendar.end_date                                      AS end_date,
       gtfs_trips.Direction_id                                     AS direction_id

FROM   gtfs_stops
       join gtfs_stop_times
         ON gtfs_stops.stop_id = gtfs_stop_times.stop_id
       join gtfs_trips
         ON gtfs_trips.trip_id = gtfs_stop_times.trip_id
       join gtfs_routes
         ON gtfs_routes.route_id = gtfs_trips.route_id
       join gtfs_calendar
         ON gtfs_calendar.service_id = gtfs_trips.service_id
       join walking_with_station_name
         ON walking_with_station_name.bus_stop_code = gtfs_stops.stop_code
WHERE  gtfs_calendar.end_date > Make_date(2016, 12, 8) /*change to current date*/
         AND  gtfs_calendar.start_date < Make_date(2016,12,16) /*change to current date*/
       AND gtfs_routes.agency_id != 2
       AND gtfs_stop_times.drop_off_only is false
       AND ( walking_with_station_name.walking_distance <= 350 )
