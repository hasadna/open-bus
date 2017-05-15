/* This query is based on all_trains_hours.sql and all_buses_near_train_stations.sql and
joins them to get the minimum waiting time for bus after a train arrives. */

/*create a table with all train times*/

WITH train_times
     AS (SELECT distinct gtfs_stops.stop_name         AS stop_name,
                gtfs_stops.stop_code         AS stop_code,
                gtfs_stop_times.arrival_time AS train_time,
                gtfs_calendar.sunday         AS train_sunday,
                gtfs_calendar.monday         AS train_monday,
                gtfs_calendar.tuesday        AS train_tuesday,
                gtfs_calendar.wednesday      AS train_wednesday,
                gtfs_calendar.thursday       AS train_thursday,
                gtfs_calendar.friday         AS train_friday,
                gtfs_calendar.saturday       AS train_saturday,
                gtfs_trips.direction_id      AS direction_id
         FROM   gtfs_stops
                join gtfs_stop_times
                  ON gtfs_stops.stop_id = gtfs_stop_times.stop_id
                join gtfs_trips
                  ON gtfs_stop_times.trip_id = gtfs_trips.trip_id
                join gtfs_routes
                  ON gtfs_routes.route_id = gtfs_trips.route_id
                join gtfs_calendar
                  ON gtfs_calendar.service_id = gtfs_trips.service_id
         WHERE  gtfs_calendar.end_date > Make_date(2016, 12, 8)
            AND gtfs_calendar.start_date <= Make_date(2016, 12, 8)
            AND gtfs_routes.agency_id = 2
            AND gtfs_stop_times.pickup_only is false) /* Not first stop */

,
  /*create a table with all bus times*/

	bus_times
     AS (SELECT station_walking_distance.train_station_code AS train_stop,
                gtfs_stop_times.arrival_time               AS bus_time,
                gtfs_routes.route_short_name               AS bus_route,
                gtfs_calendar.sunday                       AS bus_sunday,
                gtfs_calendar.monday                       AS bus_monday,
                gtfs_calendar.tuesday                      AS bus_tuesday,
                gtfs_calendar.wednesday                    AS bus_wednesday,
                gtfs_calendar.thursday                     AS bus_thursday,
                gtfs_calendar.friday                       AS bus_friday,
                gtfs_calendar.saturday                     AS bus_saturday
         FROM   gtfs_stops
                join gtfs_stop_times
                  ON gtfs_stops.stop_id = gtfs_stop_times.stop_id
                join gtfs_trips
                  ON gtfs_trips.trip_id = gtfs_stop_times.trip_id
                join gtfs_routes
                  ON gtfs_routes.route_id = gtfs_trips.route_id
                join gtfs_calendar
                  ON gtfs_calendar.service_id = gtfs_trips.service_id
                join station_walking_distance
                  ON station_walking_distance.bus_stop_code = gtfs_stops.stop_code
         WHERE gtfs_calendar.end_date > Make_date(2016, 12, 8)
            AND gtfs_calendar.start_date <= Make_date(2016, 12, 8)
            AND gtfs_routes.agency_id != 2
            AND gtfs_stop_times.drop_off_only = false
            AND station_walking_distance.distance_in_meters <= 350)

 /* Join bus time with train times */
SELECT distinct t.stop_name      AS stop_name,
       t.stop_code      AS station_code,
       t.train_time     AS train_time,
       Date_part('hour', t.train_time :: interval + '00:05'::interval) AS hour, /* adding 5 minutes for walking out of station*/
       t.train_sunday  AS sunday,
       t.train_monday  AS monday,
       t.train_tuesday  AS tuesday,
       t.train_wednesday  AS wednesday,
       t.train_thursday  AS thursday,
       t.train_friday   AS friday,
       t.train_saturday AS saturday,
       t.direction_id      AS direction_id,
       Min(bus_times.bus_time)               AS First_Bus,
       Min(Extract(epoch FROM ( bus_times.bus_time :: interval - t.train_time :: interval)) / 60)   AS waiting_time
/* get waiting time, convert to EPOCH time and back */
FROM   train_times as t
       left join bus_times
              ON t.stop_code = bus_times.train_stop
                 AND ( t.train_time :: interval + '00:05' :: interval <=
                       bus_times.bus_time ::
                           interval )
                 AND ( bus_times.bus_time :: interval <= t.train_time ::
                       interval + '02:00' :: interval )
                  /* make sure the train and bus work on the same day*/
                 AND ( ( t.train_sunday = TRUE
                         	 AND bus_times.bus_sunday = TRUE )
                        OR ( t.train_monday = TRUE
                             AND bus_times.bus_monday = TRUE )
                        OR ( t.train_tuesday = TRUE
                             AND bus_times.bus_tuesday = TRUE )
                        OR ( t.train_wednesday = TRUE
                             AND bus_times.bus_wednesday = TRUE )
                        OR ( t.train_thursday = TRUE
                             AND bus_times.bus_thursday = TRUE )
                        OR ( t.train_friday = TRUE
                             AND bus_times.bus_friday = TRUE )
                        OR ( t.train_saturday = TRUE
                             AND bus_times.bus_saturday = TRUE ) )
GROUP  BY stop_name,
        station_code, 
          train_time,
          sunday,
          monday,
          tuesday,
          wednesday,
          thursday,
          friday,
          saturday,
          direction_id
ORDER  BY stop_name,
          train_time