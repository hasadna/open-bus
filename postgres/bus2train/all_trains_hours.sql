SELECT DISTINCT
       stops.stop_name                                                AS stop_name,
       stops.stop_code                                                AS stop_code,
       stop_times.arrival_time                                        AS train_time,
       Date_part('hour', stop_times.arrival_time :: interval + '00:05'::interval) AS hour, /* adding 5 minutes for walking out of station*/
       calendar.sunday                                                AS train_sunday,
       calendar.monday                                                AS train_monday,
       calendar.tuesday                                               AS train_tuesday,
       calendar.wednesday                                             AS train_wednesday,
       calendar.thursday                                              AS train_thursday,
       calendar.friday                                                AS train_friday,
       calendar.saturday                                              AS train_saturday,
       calendar.start_date                                    AS start_date,
       calendar.end_date                                      AS end_date,
       trips.Direction_id                                             AS direction_id

FROM   stops
       join stop_times
         ON stops.stop_id = stop_times.stop_id
       join trips
         ON stop_times.trip_id = trips.trip_id
       join routes
         ON routes.route_id = trips.route_id
       join calendar
         ON calendar.service_id = trips.service_id
WHERE  calendar.end_date > Make_date(2016, 12, 8) /*change to current date*/
       AND  calendar.start_date < Make_date(2016,12,16) /*change to current date*/
       AND stop_times.pickup_only is false
       AND routes.agency_id = 2