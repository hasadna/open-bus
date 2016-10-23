## Find train stations

```sql
select distinct(stops.stop_id) from routes
join trips on trips.route_id = routes.route_id
join trip_route_story on trips.trip_id = trip_route_story.trip_id
join route_story_stops on route_story_stops.route_story_id = trip_route_story.route_story_id
join stops on route_story_stops.stop_id = stops.stop_id
where route_type=2 order by stops.stop_name;
```

or, if station_distance was run:

`select * from stops where stop_id= nearest_train_station;`

## Lines calling at a stop 

If you have stop id:

```SQL
select distinct(routes.route_id), route_short_name, route_desc from routes 
join trips on trips.route_id = routes.route_id
join stop_times on stop_times.trip_id = trips.trip_id
where stop_times.stop_id = 3559;
```

If you have stop code:

```SQL
select distinct(routes.route_id), route_short_name, route_desc from routes 
join trips on trips.route_id = routes.route_id
join stop_times on stop_times.trip_id = trips.trip_id
join stops on stop_times.stop_id = stops.stop_id
where stop_code = 42694;
```

## Trains calling at station

Get all the trains stopping at Patei Modiin, on Sunday, 2016-10-16. 

```sql
SELECT stop_times.arrival_time, routes.route_long_name 
FROM trips
JOIN stop_times ON stop_times.trip_id = trips.trip_id
JOIN calendar ON calendar.service_id = trips.service_id
JOIN routes ON routes.route_id = trips.route_id
JOIN stops ON stop_times.stop_id = stops.stop_id
WHERE stops.stop_name = 'פאתי מודיעין' 
AND calendar.sunday = TRUE
AND calendar.start_date<='2016-10-16' 
AND calendar.end_date>='2016-10-16'
ORDER BY arrival_time;
```

## Buses calling at train station

Buses calling at stops near Patei Modiin station on Sunday 2016-10-16.

Bus stop is up to 300m away from station in walking distance, according to either graph hopper or google navigation.

```sql
SELECT stop_times.arrival_time, routes.route_short_name, routes.route_desc
FROM station_walking_distance AS wd
JOIN stops AS trs ON wd.station_code = trs.stop_code
JOIN stops AS bus ON wd.stop_code = bus.stop_code
JOIN stop_times ON bus.stop_id = stop_times.stop_id
JOIN trips ON stop_times.trip_id = trips.trip_id
JOIN routes ON trips.route_id = routes.route_id
JOIN calendar ON trips.service_id = calendar.service_id
WHERE (wd.gh_walking_distance < 300 OR wd.google_walking_distance < 300)
AND calendar.sunday = True
AND calendar.start_date <= '2016-10-16'
AND calendar.end_date >= '2016-10-16'
AND trs.stop_name = 'פאתי מודיעין'
ORDER BY stop_times.arrival_time;
```
## Bus by line number and town of departure

Find route id for bus 189 starting from Holon. 

```sql
SELECT distinct(routes.route_id), routes.route_long_name, routes.route_desc FROM routes
JOIN trips ON routes.route_id = trips.route_id
JOIN stop_times ON trips.trip_id = stop_times.trip_id
JOIN stops on stop_times.stop_id = stops.stop_id
WHERE stop_sequence = 1 AND
route_short_name='189' AND
town = 'חולון';
```

## Stop where line calls

Given route_id (which you can find using the previous query)

```sql
SELECT DISTINCT stop_times.stop_id, stop_times.stop_sequence, 
                stops.stop_name, stops.town ,
                stops.stop_lat, stops.stop_lon
FROM stops
JOIN stop_times on stops.stop_id = stop_times.stop_id
join trips on stop_times.trip_id = trips.trip_id
where trips.route_id = 9813
ORDER BY stop_times.stop_sequence;
```