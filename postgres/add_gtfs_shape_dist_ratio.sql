--ALTER TABLE gtfs_stop_times ADD COLUMN shape_dist_ratio REAL;

UPDATE gtfs_stop_times
SET shape_dist_ratio = (1.0*shape_dist_traveled) /
  (SELECT MAX(shape_dist_traveled)
   FROM gtfs_stop_times a
   WHERE a.trip_id = gtfs_stop_times.trip_id);
