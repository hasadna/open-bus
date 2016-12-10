SELECT stops.stop_name                                       AS stop_name,
       stops.stop_code                                        AS stop_code,
       stop_times.arrival_time                                AS train_time,
       Date_part('hour', stop_times.arrival_time :: interval) AS hour,
       calendar.sunday                                        AS train_sunday,
       calendar.monday                                        AS train_monday,
       calendar.tuesday                                       AS train_tuesday,
       calendar.wednesday                                     AS train_wednesday,
       calendar.thursday                                      AS train_thursday,
       calendar.friday                                        AS train_friday,
       calendar.saturday                                      AS train_saturday
FROM   stops
       join stop_times
         ON stops.stop_id = stop_times.stop_id
       join trips
         ON stop_times.trip_id = trips.trip_id
       join routes
         ON routes.route_id = trips.route_id
       join calendar
         ON calendar.service_id = trips.service_id
WHERE  calendar.end_date > Make_date(2016, 11, 4) /*change to current date*/
       AND routes.agency_id = 2  