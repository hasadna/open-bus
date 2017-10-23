-- Query adding a table of shapes as line objects (see issue #29)
-- The query creates a point object from the shape point coordinates. Than it groups all the points by shape id, orders them and creates a line from them.
-- All lines are stored in gtfs_shape_lines table
DROP TABLE IF EXISTS gtfs_shape_lines;

CREATE TABLE gtfs_shape_lines AS
  (SELECT tmp.shape_id, St_makeline(St_setsrid(St_makepoint(shape_pt_lon, shape_pt_lat), 4326)) AS shape_line
   FROM   (SELECT *
           FROM   gtfs_shapes
           ORDER  BY shape_pt_sequence) AS tmp
   GROUP  BY tmp.shape_id
);
