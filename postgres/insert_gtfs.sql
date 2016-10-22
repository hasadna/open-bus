-- run timing to see how much time everything takes
\timing


-- drop old tables
DROP TABLE IF EXISTS agency;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS stop_times;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS shapes;

---- agencies ----
\echo ********** importing agencies **********

CREATE TABLE agency
(
  agency_id   INTEGER                NOT NULL,
  agency_name CHARACTER VARYING(100) NOT NULL,
  CONSTRAINT agency_pkey PRIMARY KEY (agency_id)
);
ALTER TABLE agency
  OWNER TO obus;

\copy agency from '/tmp/gtfs/agency_for_db.txt' DELIMITER ',' CSV HEADER;


-- routes --
\echo ********** importing routes **********

CREATE TABLE routes
(
  route_id         INTEGER NOT NULL,
  agency_id        INTEGER,
  route_short_name CHARACTER VARYING(50),
  route_long_name  CHARACTER VARYING(255),
  route_desc       CHARACTER VARYING(10),
  route_type       INTEGER NOT NULL, -- Should be an Enum.
  route_color      CHARACTER VARYING(9) -- Can be an Enum.

);
ALTER TABLE routes
  OWNER TO obus;



\copy routes from '/tmp/gtfs/routes.txt' DELIMITER ',' CSV HEADER;


ALTER TABLE routes
  ADD CONSTRAINT routes_pkey PRIMARY KEY (route_id);
CREATE INDEX routes_agency_id
  ON routes
  USING BTREE
  (agency_id);
CREATE INDEX routes_route_type
  ON routes
  USING BTREE
  (route_type);

-- stops --
\echo ********** importing stops **********

CREATE TABLE stops
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
ALTER TABLE stops
  OWNER TO obus;

\copy stops(stop_id, stop_code, stop_name, stop_desc, stop_lat, stop_lon, location_type, parent_station, zone_id) from '/tmp/gtfs/stops.txt' DELIMITER ',' CSV HEADER;

UPDATE stops
SET address = left(trim(split_part(stop_desc, ':', 2)), -4),
  town      = left(trim(split_part(stop_desc, ':', 3)), -5);

ALTER TABLE stops
  ADD CONSTRAINT stops_pkey PRIMARY KEY (stop_id);

CREATE INDEX stops_stop_code
  ON stops
  USING BTREE
  (stop_code);
CREATE INDEX stops_location_type
  ON stops
  USING BTREE
  (location_type);
CREATE INDEX stops_parent_station
  ON stops
  USING BTREE
  (parent_station);
CREATE INDEX stops_zone_id
  ON stops
  USING BTREE
  (zone_id COLLATE pg_catalog."default");
CREATE INDEX stops_town
  ON stops
  USING BTREE
  (town);

--select COUNT(DISTINCT town) from stops;

-- trips --
\echo ********** importing trips **********

CREATE TABLE trips
(
  route_id     INTEGER,
  service_id   INTEGER,
  trip_id      CHARACTER VARYING(50) NOT NULL,
  direction_id INTEGER,
  shape_id     INTEGER
);
ALTER TABLE trips
  OWNER TO obus;

\copy trips from '/tmp/gtfs/trips.txt' DELIMITER ',' CSV HEADER;


ALTER TABLE trips
  ADD CONSTRAINT trips_pkey PRIMARY KEY (trip_id);
CREATE INDEX trips_direction_id
  ON trips
  USING BTREE
  (direction_id);
CREATE INDEX trips_route_id
  ON trips
  USING BTREE
  (route_id);
CREATE INDEX trips_service_id
  ON trips
  USING BTREE
  (service_id);
CREATE INDEX trips_shape_id
  ON trips
  USING BTREE
  (shape_id);

-- calendar --
\echo ********** importing calendar **********
CREATE TABLE calendar
(
  service_id INTEGER NOT NULL,
  sunday     BOOLEAN,
  monday     BOOLEAN,
  tuesday    BOOLEAN,
  wednesday  BOOLEAN,
  thursday   BOOLEAN,
  friday     BOOLEAN,
  saturday   BOOLEAN,
  start_date CHARACTER VARYING(8),
  end_date   CHARACTER VARYING(8)
);
ALTER TABLE calendar
  OWNER TO obus;

\copy calendar from '/tmp/gtfs/calendar.txt' DELIMITER ',' CSV HEADER;


ALTER TABLE calendar
  ADD CONSTRAINT calendar_pkey PRIMARY KEY (service_id);
CREATE INDEX calendar_service_id
  ON calendar
  USING BTREE
  (service_id);

-- stop_times --
\echo ********** importing stop times **********

CREATE TABLE stop_times
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
ALTER TABLE stop_times
  OWNER TO obus;

\copy stop_times from '/tmp/gtfs/stop_times.txt' DELIMITER ',' CSV HEADER;

-- renamed the fields to something more self explanatory
-- It's not a mistake! see GTFS documentation.
ALTER TABLE stop_times RENAME pickup_type TO drop_off_only;
ALTER TABLE stop_times RENAME drop_off_type TO pickup_only;


-- indexes are very expensive on this huge table, so let's only create indexes we need we know
CREATE INDEX stop_times_trip_id
  ON stop_times
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


-- shapes --
\echo ********** importing shapes **********

CREATE TABLE shapes
(
  shape_id          INTEGER       NOT NULL,
  shape_pt_lat      NUMERIC(8, 6) NOT NULL,
  shape_pt_lon      NUMERIC(8, 6) NOT NULL,
  shape_pt_sequence INTEGER       NOT NULL
);
ALTER TABLE shapes
  OWNER TO obus;

\copy shapes from '/tmp/gtfs/shapes.txt' DELIMITER ',' CSV HEADER;

ALTER TABLE shapes
  ADD CONSTRAINT shapes_pkey PRIMARY KEY (shape_id, shape_pt_sequence);

-- make sure re:dash can access the new tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO redash;
