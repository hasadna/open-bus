-- run timing to see how much time everything takes
\timing


-- drop old tables
DROP TABLE IF EXISTS gtfs_agency;
DROP TABLE IF EXISTS gtfs_routes;
DROP TABLE IF EXISTS gtfs_trips;
DROP TABLE IF EXISTS gtfs_calendar;
DROP TABLE IF EXISTS gtfs_stop_times;
DROP TABLE IF EXISTS gtfs_stops;
DROP TABLE IF EXISTS gtfs_shapes;

---- agencies ----
\echo ********** importing agencies **********

CREATE TABLE gtfs_agency
(
  agency_id   INTEGER                NOT NULL,
  agency_name CHARACTER VARYING(100) NOT NULL,
  CONSTRAINT agency_pkey PRIMARY KEY (agency_id)
);
ALTER TABLE gtfs_agency
  OWNER TO obus;

\copy gtfs_agency from '/tmp/gtfs/agency_for_db.txt' DELIMITER ',' CSV HEADER;


-- routes --
\echo ********** importing routes **********

CREATE TABLE gtfs_routes
(
  route_id         INTEGER NOT NULL,
  agency_id        INTEGER,
  route_short_name CHARACTER VARYING(50),
  route_long_name  CHARACTER VARYING(255),
  route_desc       CHARACTER VARYING(10),
  route_type       INTEGER NOT NULL, -- Should be an Enum.
  route_color      CHARACTER VARYING(9) -- Can be an Enum.

);
ALTER TABLE gtfs_routes
  OWNER TO obus;



\copy gtfs_routes from '/tmp/gtfs/routes.txt' DELIMITER ',' CSV HEADER;


ALTER TABLE gtfs_routes
  ADD CONSTRAINT routes_pkey PRIMARY KEY (route_id);
CREATE INDEX routes_agency_id
  ON gtfs_routes
  USING BTREE
  (agency_id);
CREATE INDEX routes_route_type
  ON gtfs_routes
  USING BTREE
  (route_type);

-- stops --
\echo ********** importing stops **********

CREATE TABLE gtfs_stops
(
  stop_id        INTEGER NOT NULL,
  stop_code      INTEGER NOT NULL,
  stop_name      CHARACTER VARYING(255),
  stop_desc      CHARACTER VARYING(255),
  stop_lat       NUMERIC(10, 8), -- TODO: check requested type-size.
  stop_lon       NUMERIC(10, 8), -- TODO: check requested type-size.
  location_type  BOOLEAN, -- Should be an Enum.
  parent_station INTEGER, -- Should be an Enum.
  zone_id        CHARACTER VARYING(255),
  address        CHARACTER VARYING(50),
  town           CHARACTER VARYING(50)
);
ALTER TABLE gtfs_stops
  OWNER TO obus;

\copy gtfs_stops(stop_id, stop_code, stop_name, stop_desc, stop_lat, stop_lon, location_type, parent_station, zone_id) from '/tmp/gtfs/stops.txt' DELIMITER ',' CSV HEADER;

UPDATE gtfs_stops
SET address = left(trim(split_part(stop_desc, ':', 2)), -4),
  town      = left(trim(split_part(stop_desc, ':', 3)), -5);

ALTER TABLE gtfs_stops
  ADD CONSTRAINT stops_pkey PRIMARY KEY (stop_id);

CREATE INDEX stops_stop_code
  ON gtfs_stops
  USING BTREE
  (stop_code);
CREATE INDEX stops_location_type
  ON gtfs_stops
  USING BTREE
  (location_type);
CREATE INDEX stops_parent_station
  ON gtfs_stops
  USING BTREE
  (parent_station);
CREATE INDEX stops_zone_id
  ON gtfs_stops
  USING BTREE
  (zone_id COLLATE pg_catalog."default");
CREATE INDEX stops_town
  ON gtfs_stops
  USING BTREE
  (town);

--select COUNT(DISTINCT town) from stops;

-- trips --
\echo ********** importing trips **********

CREATE TABLE gtfs_trips
(
  route_id     INTEGER,
  service_id   INTEGER,
  trip_id      CHARACTER VARYING(50) NOT NULL,
  direction_id INTEGER,
  shape_id     INTEGER
);
ALTER TABLE gtfs_trips
  OWNER TO obus;

\copy gtfs_trips from '/tmp/gtfs/trips.txt' DELIMITER ',' CSV HEADER;


ALTER TABLE gtfs_trips
  ADD CONSTRAINT trips_pkey PRIMARY KEY (trip_id);
CREATE INDEX trips_direction_id
  ON gtfs_trips
  USING BTREE
  (direction_id);
CREATE INDEX trips_route_id
  ON gtfs_trips
  USING BTREE
  (route_id);
CREATE INDEX trips_service_id
  ON gtfs_trips
  USING BTREE
  (service_id);
CREATE INDEX trips_shape_id
  ON gtfs_trips
  USING BTREE
  (shape_id);

-- calendar --
\echo ********** importing calendar **********
CREATE TABLE gtfs_calendar
(
  service_id INTEGER NOT NULL,
  sunday     BOOLEAN,
  monday     BOOLEAN,
  tuesday    BOOLEAN,
  wednesday  BOOLEAN,
  thursday   BOOLEAN,
  friday     BOOLEAN,
  saturday   BOOLEAN,
  start_date date,
  end_date   date
);
ALTER TABLE gtfs_calendar
  OWNER TO obus;

\copy gtfs_calendar from '/tmp/gtfs/calendar.txt' DELIMITER ',' CSV HEADER;


ALTER TABLE gtfs_calendar
  ADD CONSTRAINT calendar_pkey PRIMARY KEY (service_id);
CREATE INDEX calendar_service_id
  ON gtfs_calendar
  USING BTREE
  (service_id);

-- stop_times --
\echo ********** importing stop times **********

CREATE TABLE gtfs_stop_times
(
  trip_id             CHARACTER VARYING(50),
  arrival_time        CHARACTER VARYING(8),
  departure_time      CHARACTER VARYING(8),
  stop_id             INTEGER,
  stop_sequence       INTEGER,
  pickup_type         BOOLEAN,
  drop_off_type       BOOLEAN,
  shape_dist_traveled INTEGER

);
ALTER TABLE gtfs_stop_times
  OWNER TO obus;

\copy gtfs_stop_times from '/tmp/gtfs/stop_times.txt' DELIMITER ',' CSV HEADER;

-- renamed the fields to something more self explanatory
-- It's not a mistake! see GTFS documentation.
ALTER TABLE gtfs_stop_times RENAME pickup_type TO drop_off_only;
ALTER TABLE gtfs_stop_times RENAME drop_off_type TO pickup_only;


-- indexes are very expensive on this huge table, so let's only create indexes we need we know
CREATE INDEX stop_times_trip_id
  ON gtfs_stop_times
  USING BTREE
  (trip_id);

--CREATE INDEX stop_times_stop_id
--  ON stop_times
--  USING btree
--  (stop_id );

-- CREATE INDEX stop_times_stop_sequence
--   ON stop_times
--   USING btree
--   (stop_sequence );


-- Calculate the ratio of distance that was traveled. See issue #33 for more information
ALTER TABLE gtfs_stop_times ADD COLUMN shape_dist_ratio REAL;

UPDATE gtfs_stop_times
SET shape_dist_ratio = (1.0*shape_dist_traveled) /
  (SELECT MAX(shape_dist_traveled)
   FROM gtfs_stop_times a
WHERE a.trip_id = gtfs_stop_times.trip_id);

-- shapes --
\echo ********** importing shapes **********

CREATE TABLE gtfs_shapes
(
  shape_id          INTEGER       NOT NULL,
  shape_pt_lat      NUMERIC(8, 6) NOT NULL,
  shape_pt_lon      NUMERIC(8, 6) NOT NULL,
  shape_pt_sequence INTEGER       NOT NULL
);
ALTER TABLE gtfs_shapes
  OWNER TO obus;

\copy gtfs_shapes from '/tmp/gtfs/shapes.txt' DELIMITER ',' CSV HEADER;

ALTER TABLE gtfs_shapes
  ADD CONSTRAINT shapes_pkey PRIMARY KEY (shape_id, shape_pt_sequence);

-- make sure re:dash can access the new tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO redash;

INSERT INTO gtfs_update_history(update_date,gtfs_date) VALUES (current_timestamp, make_date(:v1,:v2,:v3));