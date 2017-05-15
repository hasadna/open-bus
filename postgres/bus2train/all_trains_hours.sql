SELECT DISTINCT
       gtfs_stops.stop_name                                                AS stop_name,
       gtfs_stops.stop_code                                                AS stop_code,
       gtfs_stop_times.arrival_time                                        AS train_time,
       Date_part('hour', gtfs_stop_times.arrival_time :: interval + '00:05'::interval) AS hour, /* adding 5 minutes for walking out of station*/
       gtfs_calendar.sunday                                                AS train_sunday,
       gtfs_calendar.monday                                                AS train_monday,
       gtfs_calendar.tuesday                                               AS train_tuesday,
       gtfs_calendar.wednesday                                             AS train_wednesday,
       gtfs_calendar.thursday                                              AS train_thursday,
       gtfs_calendar.friday                                                AS train_friday,
       gtfs_calendar.saturday                                              AS train_saturday,
       gtfs_calendar.start_date                                    AS start_date,
       gtfs_calendar.end_date                                      AS end_date,
       gtfs_trips.Direction_id                                             AS direction_id

FROM   gtfs_stops
       join gtfs_stop_times
         ON gtfs_stops.stop_id = gtfs_stop_times.stop_id
       join gtfs_trips
         ON gtfs_stop_times.trip_id = gtfs_trips.trip_id
       join gtfs_routes
         ON gtfs_routes.route_id = gtfs_trips.route_id
       join gtfs_calendar
         ON gtfs_calendar.service_id = gtfs_trips.service_id
WHERE  gtfs_calendar.end_date > Make_date(2016, 12, 8) /*change to current date*/
       AND  gtfs_calendar.start_date < Make_date(2016,12,16) /*change to current date*/
       AND gtfs_stop_times.pickup_only is false
       AND gtfs_routes.agency_id = 2