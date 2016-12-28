/* create walking distance table with train station name and min walking distance */
 WITH walking_with_station_name
     AS (SELECT station_walking_distance.bus_stop_code,
                station_walking_distance.train_station_code,
                Min(station_walking_distance.distance_in_meters) AS
                walking_distance,
                stops.stop_name
         FROM   station_walking_distance
                join stops
                  ON station_walking_distance.train_station_code =
                     stops.stop_code
         GROUP  BY bus_stop_code,
                   train_station_code,
                   stop_name)

/* extract all bus times near train station */
SELECT DISTINCT
       walking_with_station_name.train_station_code           AS train_stop,
       walking_with_station_name.stop_name                    AS train_stop_name,
       stops.stop_name                                        AS bus_stop_name,
       Date_part('hour', stop_times.arrival_time :: interval) AS hour,
       stop_times.arrival_time                              AS bus_time,
       routes.route_short_name                                AS bus_route,
       calendar.sunday                                        AS bus_sunday,
       calendar.monday                                        AS bus_monday,
       calendar.tuesday                                       AS bus_tuesday,
       calendar.wednesday                                     AS bus_wednesday,
       calendar.thursday                                      AS bus_thursday,
       calendar.friday                                        AS bus_friday,
       calendar.saturday                                      AS bus_saturday,
       routes.route_desc                                      AS bus_route_makat,
       calednar.start_date                                    AS start_date,
       calendar.end_date                                      AS end_date,
       trips.Direction_id                                     AS direction_id

FROM   stops
       join stop_times
         ON stops.stop_id = stop_times.stop_id
       join trips
         ON trips.trip_id = stop_times.trip_id
       join routes
         ON routes.route_id = trips.route_id
       join calendar
         ON calendar.service_id = trips.service_id
       join walking_with_station_name
         ON walking_with_station_name.bus_stop_code = stops.stop_code
WHERE  calendar.end_date > Make_date(2016, 12, 8) /*change to current date*/
         AND  calendar.start_date < Make_date(2016,12,16) /*change to current date*/
       AND routes.agency_id != 2
       AND stop_times.drop_off_only is false
       AND ( walking_with_station_name.walking_distance <= 350 )
