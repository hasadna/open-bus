--query adding vehicle_location_point to siri_arrivals (see issue #30)

-- Create column:
SELECT AddGeometryColumn ('siri_arrivals','vehicle_location_point',4326,'POINT',2);

--Populate data:
update siri_arrivals 
set vehicle_location_point = ST_SetSRID(ST_MakePoint(cast(vehicle_location_lon as double precision), cast(vehicle_location_lat as double precision)),4326)
where vehicle_location_lon !='';

-- Query adding a table of shapes as line objects (see issue #29)
-- The query creates a point object from the shape point coordinates. Than it groups all the points by shape id, orders them and creates a line from them.
-- All lines are stored in gtfs_shape_lines table
CREATE TABLE gtfs_shape_lines AS
  (SELECT tmp.shape_id, St_makeline(St_setsrid(St_makepoint(shape_pt_lon, shape_pt_lat), 4326)) AS shape_line
   FROM   (SELECT *
           FROM   gtfs_shapes
           ORDER  BY shape_pt_sequence) AS tmp
   GROUP  BY tmp.shape_id
  );  
  
  
-- Add route offset to siri_arrivals (see issue #26)
--Adding offset column 
ALTER TABLE siri_arrivals
ADD route_offset float8;

-- Populate data 
with join_result as (SELECT id, ST_LineLocatePoint(shape_line, siri_arrivals.vehicle_location_point) as line_locate_point_value
FROM siri_arrivals
JOIN gtfs_trips ON gtfs_trips.trip_id = siri_arrivals.trip_id_from_gtfs
JOIN gtfs_shape_lines ON gtfs_trips.shape_id = gtfs_shape_lines.shape_id)
 
update siri_arrivals 
set route_offset = join_result.line_locate_point_value
from join_result
where siri_arrivals.id = join_result.id

