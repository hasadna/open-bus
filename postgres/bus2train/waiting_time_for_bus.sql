/* This query is based on all_trains_hours.sql and all_buses_near_train_stations.sql and
joins them to get the minimum waiting time for bus after a train arrives. */

/*create a table with all train times*/

WITH train_times
     AS (SELECT distinct stops.stop_name         AS stop_name,
                stops.stop_code         AS stop_code,
                stop_times.arrival_time AS train_time,
                calendar.sunday         AS train_sunday,
                calendar.monday         AS train_monday,
                calendar.tuesday        AS train_tuesday,
                calendar.wednesday      AS train_wednesday,
                calendar.thursday       AS train_thursday,
                calendar.friday         AS train_friday,
                calendar.saturday       AS train_saturday,
                trips.direction_id      AS direction_id
         FROM   stops
                join stop_times
                  ON stops.stop_id = stop_times.stop_id
                join trips
                  ON stop_times.trip_id = trips.trip_id
                join routes
                  ON routes.route_id = trips.route_id
                join calendar
                  ON calendar.service_id = trips.service_id
         WHERE  calendar.end_date > Make_date(2016, 12, 8)
            AND calendar.start_date <= Make_date(2016, 12, 8)
            AND routes.agency_id = 2
            AND stop_times.pickup_only is false) /* Not first stop */

,
  /*create a table with all bus times*/

	bus_times
     AS (SELECT station_walking_distance.train_station_code AS train_stop,
                stop_times.arrival_time               AS bus_time,
                routes.route_short_name               AS bus_route,
                calendar.sunday                       AS bus_sunday,
                calendar.monday                       AS bus_monday,
                calendar.tuesday                      AS bus_tuesday,
                calendar.wednesday                    AS bus_wednesday,
                calendar.thursday                     AS bus_thursday,
                calendar.friday                       AS bus_friday,
                calendar.saturday                     AS bus_saturday
         FROM   stops
                join stop_times
                  ON stops.stop_id = stop_times.stop_id
                join trips
                  ON trips.trip_id = stop_times.trip_id
                join routes
                  ON routes.route_id = trips.route_id
                join calendar
                  ON calendar.service_id = trips.service_id
                join station_walking_distance
                  ON station_walking_distance.bus_stop_code = stops.stop_code
         WHERE calendar.end_date > Make_date(2016, 12, 8)
            AND calendar.start_date <= Make_date(2016, 12, 8)
            AND routes.agency_id != 2
            AND stop_times.drop_off_only = false
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