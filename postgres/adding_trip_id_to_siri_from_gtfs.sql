-- For more information about this query, refer to issue #24
-- Note: running this query on open-bus server won't work on a big table of siri_arrivals due to lack of memory. Can run up to 3 million row at a time.
-- Later we will use this query when each siri response is received.

ALTER TABLE siri_arrivals ADD COLUMN IF NOT EXISTS trip_id_from_gtfs varchar(20);

WITH SIRI_GTFS
     AS (

select *

-- SIRI, with additional computed fields:
-- formatted_date: planned departure, truncated to date
-- dow_int: integer representing day of week (0-sun, 6-sat)
-- formatted_time: planned departure, truncated to time of day
from 
    (select *,
        date_trunc('day', origin_aimed_departure_time) as siri_departure_date,
         extract (dow from origin_aimed_departure_time)::int as siri_dow_int,
         to_char (origin_aimed_departure_time AT TIME ZONE 'IST', 'HH24:MI:SS') as siri_departure_time
    from siri_arrivals
-- added to decrease size of query. will run daily.
    where Recorded_at_time::date = make_date(:v3,:v2,:v1) and vehicle_location_lat is not null
    ) as siri

join


-- Joined GTFS for relevant fields, taken from issue 24
    (select route_id, gtfs_stop_times.trip_id, DEPARTURE_TIME, sunday, monday, tuesday, wednesday, thursday, friday, saturday, start_date, end_date
    from gtfs_trips 
    join gtfs_stop_times on gtfs_stop_times.trip_id = gtfs_trips.trip_id
    join gtfs_calendar on gtfs_calendar.service_id = gtfs_trips.service_id
--    where route_id = 7020 -- commented out, used for debugging and reducing datasize
    and stop_sequence= 1) as gtfs
    
-- We joined GTFS with SIRI on:
-- SIRI time of departure must match exactly time of departure of GTFS (See comment in issue 24)
-- SIRI date of departure must be included in time interval of GTFS
-- SIRI day of week must match 'sunday' to 'saturday' fields in GTFS
on gtfs.route_id = siri.line_ref 
and gtfs.DEPARTURE_TIME = siri_departure_time 
and (siri_dow_int = 0 and gtfs.sunday = true
    or siri_dow_int = 1 and gtfs.monday = true
    or siri_dow_int = 2 and gtfs.tuesday = true
    or siri_dow_int = 3 and gtfs.wednesday = true
    or siri_dow_int = 4 and gtfs.thursday = true
    or siri_dow_int = 5 and gtfs.friday = true
    or siri_dow_int = 6 and gtfs.saturday = true)
and siri_departure_date >= gtfs.start_date and siri_departure_date <= gtfs.end_date
-- where siri_departure_date = '2017-01-02'::date -- commented out, used for debugging and reducing datasize
)

UPDATE siri_arrivals
SET trip_id_from_gtfs =  SIRI_GTFS.trip_id
from SIRI_GTFS
where siri_gtfs.id = siri_arrivals.id
