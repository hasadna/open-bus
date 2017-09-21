-- make sure you invoke the query with :v3,:v2,:v1
with join_result as (SELECT id, ST_LineLocatePoint(shape_line, ST_SetSRID(ST_MakePoint(cast(vehicle_location_lon as double precision), cast(vehicle_location_lat as double precision)),4326)) as line_locate_point_value
FROM siri_arrivals
JOIN gtfs_trips ON gtfs_trips.trip_id = siri_arrivals.trip_id_from_gtfs
JOIN gtfs_shape_lines ON gtfs_trips.shape_id = gtfs_shape_lines.shape_id
where vehicle_location_lon is not null and Recorded_at_time::date = make_date(:v3,:v2,:v1))

update siri_arrivals
set route_offset = join_result.line_locate_point_value
from join_result
where siri_arrivals.id = join_result.id