## Find train stations

```sql
select distinct(gtfs_stops.stop_id) from gtfs_routes
join gtfs_trips on gtfs_trips.route_id = gtfs_routes.route_id
join trip_route_story on gtfs_trips.trip_id = trip_route_story.trip_id
join route_story_stops on route_story_stops.route_story_id = trip_route_story.route_story_id
join gtfs_stops on route_story_stops.stop_id = gtfs_stops.stop_id
where route_type=2 order by gtfs_stops.stop_name;
```

or, if station_distance was run:

`select * from stops where stop_id= nearest_train_station;`

## Lines calling at a stop 

If you have stop id:

```SQL
select distinct(gtfs_routes.route_id), route_short_name, route_desc from gtfs_routes 
join gtfs_trips on gtfs_trips.route_id = gtfs_routes.route_id
join gtfs_stop_times on gtfs_stop_times.trip_id = gtfs_trips.trip_id
where gtfs_stop_times.stop_id = 3559;
```

If you have stop code:

```SQL
select distinct(gtfs_routes.route_id), route_short_name, route_desc from gtfs_routes 
join gtfs_trips on gtfs_trips.route_id = gtfs_routes.route_id
join gtfs_stop_times on gtfs_stop_times.trip_id = gtfs_trips.trip_id
join gtfs_stops on gtfs_stop_times.stop_id = gtfs_stops.stop_id
where stop_code = 42694;
```

## Trains calling at station

Get all the trains stopping at Patei Modiin, on Sunday, 2016-10-16. 

```sql
SELECT gtfs_stop_times.arrival_time, gtfs_routes.route_long_name 
FROM gtfs_trips
JOIN gtfs_stop_times ON gtfs_stop_times.trip_id = gtfs_trips.trip_id
JOIN gtfs_calendar ON gtfs_calendar.service_id = gtfs_trips.service_id
JOIN gtfs_routes ON gtfs_routes.route_id = gtfs_trips.route_id
JOIN gtfs_stops ON gtfs_stop_times.stop_id = gtfs_stops.stop_id
WHERE gtfs_stops.stop_name = 'פאתי מודיעין' 
AND gtfs_calendar.sunday = TRUE
AND gtfs_calendar.start_date<='2016-10-16' 
AND gtfs_calendar.end_date>='2016-10-16'
ORDER BY arrival_time;
```

## Buses calling at train station

Buses calling at stops near Patei Modiin station on Sunday 2016-10-16.

Bus stop is up to 300m away from station in walking distance, according to either graph hopper or google navigation.

```sql
SELECT gtfs_stop_times.arrival_time, gtfs_routes.route_short_name, gtfs_routes.route_desc
FROM station_walking_distance AS wd
JOIN gtfs_stops AS trs ON wd.station_code = trs.stop_code
JOIN gtfs_stops AS bus ON wd.stop_code = bus.stop_code
JOIN gtfs_stop_times ON bus.stop_id = gtfs_stop_times.stop_id
JOIN gtfs_trips ON gtfs_stop_times.trip_id = gtfs_trips.trip_id
JOIN gtfs_routes ON gtfs_trips.route_id = gtfs_routes.route_id
JOIN gtfs_calendar ON gtfs_trips.service_id = gtfs_calendar.service_id
WHERE (wd.gh_walking_distance < 300 OR wd.google_walking_distance < 300)
AND gtfs_calendar.sunday = True
AND gtfs_calendar.start_date <= '2016-10-16'
AND gtfs_calendar.end_date >= '2016-10-16'
AND trs.stop_name = 'פאתי מודיעין'
ORDER BY gtfs_stop_times.arrival_time;
```
## Bus by line number and town of departure

Find route id for bus 189 starting from Holon. 

```sql
SELECT distinct(gtfs_routes.route_id), gtfs_routes.route_long_name, gtfs_routes.route_desc FROM gtfs_routes
JOIN gtfs_trips ON gtfs_routes.route_id = gtfs_trips.route_id
JOIN gtfs_stop_times ON gtfs_trips.trip_id = gtfs_stop_times.trip_id
JOIN gtfs_stops on gtfs_stop_times.stop_id = gtfs_stops.stop_id
WHERE stop_sequence = 1 AND
route_short_name='189' AND
town = 'חולון';
```

Bus by line number and passing through town

```sql
SELECT gtfs_routes.route_id, gtfs_routes.route_short_name, gtfs_routes.route_long_name, gtfs_routes.route_desc FROM gtfs_routes
JOIN gtfs_trips ON gtfs_routes.route_id = gtfs_trips.route_id
JOIN gtfs_stop_times ON gtfs_trips.trip_id = gtfs_stop_times.trip_id
JOIN gtfs_stops on gtfs_stop_times.stop_id = gtfs_stops.stop_id
WHERE gtfs_stops.town = 'חולון' 
AND gtfs_routes.route_short_name = '189'
GROUP BY gtfs_routes.route_id, gtfs_routes.route_long_name, gtfs_routes.route_desc;
```

## Stop where line calls

Given route_id (which you can find using the previous query)

```sql
SELECT DISTINCT gtfs_stop_times.stop_id, gtfs_stop_times.stop_sequence, 
                gtfs_stops.stop_name, gtfs_stops.town ,
                gtfs_stops.stop_lat, gtfs_stops.stop_lon
FROM gtfs_stops
JOIN gtfs_stop_times on stops.stop_id = gtfs_stop_times.stop_id
join gtfs_trips on gtfs_stop_times.trip_id = gtfs_trips.trip_id
where gtfs_trips.route_id = 9813
ORDER BY gtfs_stop_times.stop_sequence;
```
## Number of daily trips per route

Given route_id (which you can find using the previous query).

Remember that because of alternatives, there might be two routes with the same line number, doing almost the same route.

```sql
SELECT  gtfs_routes.route_short_name, gtfs_routes.route_long_name, 
	count(CASE WHEN gtfs_calendar.sunday THEN 1 END) as SUNDAY,
	count(CASE WHEN gtfs_calendar.monday THEN 1 END) as MONDAY,
	count(CASE WHEN gtfs_calendar.tuesday THEN 1 END) as TUESDAY,
    count(CASE WHEN gtfs_calendar.wednesday THEN 1 END) as WEDNESDAY,
    count(CASE WHEN gtfs_calendar.thursday THEN 1 END) as THURSDAY,
    count(CASE WHEN gtfs_calendar.friday THEN 1 END) as FRIDAY,
    count(CASE WHEN gtfs_calendar.saturday THEN 1 END) as SATURDAY
FROM gtfs_calendar
JOIN gtfs_trips ON gtfs_trips.service_id = gtfs_calendar.service_id
JOIN gtfs_routes ON gtfs_routes.route_id = gtfs_trips.route_id
where gtfs_trips.route_id = 9813
GROUP BY gtfs_routes.route_id;
```



