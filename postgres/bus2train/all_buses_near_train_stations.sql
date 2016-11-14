 WITH walking_with_station_name
     AS (SELECT station_walking_distance.stop_code,
                station_walking_distance.station_code,
                station_walking_distance.google_walking_distance,
                station_walking_distance.gh_walking_distance,
                stops.stop_name
         FROM   station_walking_distance
                join stops
                  ON station_walking_distance.station_code = stops.stop_code)
SELECT walking_with_station_name.station_code                         AS train_stop,
       walking_with_station_name.stop_name                            AS train_stop_name,
       stops.stop_name                                        AS bus_stop_name,
       Date_part('hour', stop_times.arrival_time :: interval) AS hour,
       stop_times.arrival_time                                AS bus_time,
       routes.route_short_name                                AS bus_route,
       calendar.sunday                                        AS bus_sunday,
       calendar.monday                                        AS bus_monday,
       calendar.tuesday                                       AS bus_tuesday,
       calendar.wednesday                                     AS bus_wednesday,
       calendar.thursday                                      AS bus_thursday,
       calendar.friday                                        AS bus_friday,
       calendar.saturday                                      AS bus_saturday
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
         ON walking_with_station_name.stop_code = stops.stop_code
WHERE  calendar.end_date > Make_date(2016, 11, 4) /*change to current date*/
       AND routes.agency_id != 2
       AND ( walking_with_station_name.google_walking_distance <= 300
              OR walking_with_station_name.gh_walking_distance <= 300 )  