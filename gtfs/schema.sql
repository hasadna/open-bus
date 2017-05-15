-- TODO: Create enums for relevant fields (inline comments).
-- TODO: Make sure type-sizes are fine.
-- TODO: Check requested type-size for coordinates.
-- TODO: Check requested type-size for shape_dist_traveled.
SET ROLE obus;

CREATE TABLE gtfs_agency
(
  agency_id integer NOT NULL,
  agency_name character varying(100) NOT NULL,
  CONSTRAINT agency_pkey PRIMARY KEY (agency_id )
);
ALTER TABLE gtfs_agency
  OWNER TO obus;


CREATE TABLE gtfs_routes
(
  route_id integer NOT NULL,
  agency_id integer,
  route_short_name character varying(50),
  route_long_name character varying(255),
  route_desc character varying(10),
  route_type integer NOT NULL, -- Should be an Enum.
  route_color character varying(9), -- Can be an Enum.
  CONSTRAINT routes_pkey PRIMARY KEY (route_id )
);
ALTER TABLE gtfs_routes
  OWNER TO obus;
CREATE INDEX routes_agency_id
  ON gtfs_routes
  USING btree
  (agency_id );
CREATE INDEX routes_route_type
  ON gtfs_routes
  USING btree
  (route_type );

  
CREATE TABLE gtfs_trips
(
  trip_id character varying(50) NOT NULL,
  route_id integer,
  service_id integer,
  direction_id integer,
  shape_id integer,
  CONSTRAINT trips_pkey PRIMARY KEY (trip_id )
);
ALTER TABLE gtfs_trips
  OWNER TO obus;
CREATE INDEX trips_direction_id
  ON gtfs_trips
  USING btree
  (direction_id );
CREATE INDEX trips_route_id
  ON gtfs_trips
  USING btree
  (route_id );
CREATE INDEX trips_service_id
  ON gtfs_trips
  USING btree
  (service_id );
CREATE INDEX trips_shape_id
  ON gtfs_trips
  USING btree
  (shape_id );

  
CREATE TABLE gtfs_calendar
(
  service_id integer NOT NULL,
  sunday boolean,
  monday boolean,
  tuesday boolean,
  wednesday boolean,
  thursday boolean,
  friday boolean,
  saturday boolean,
  start_date character varying(8),
  end_date character varying(8),
  CONSTRAINT calendar_pkey PRIMARY KEY (service_id )
);
ALTER TABLE gtfs_calendar
  OWNER TO obus;
CREATE INDEX calendar_service_id
  ON gtfs_calendar
  USING btree
  (service_id ); 
  
  
CREATE TABLE gtfs_stop_times
(
  id serial NOT NULL,
  trip_id character varying(50),
  arrival_time character varying(8),
  departure_time character varying(8),
  stop_id integer,
  stop_sequence integer,
  pickup_type boolean,
  drop_off_type boolean,
  CONSTRAINT stop_times_pkey PRIMARY KEY (id )
);
ALTER TABLE gtfs_stop_times
  OWNER TO obus;
CREATE INDEX stop_times_drop_off_type
  ON gtfs_stop_times
  USING btree
  (drop_off_type );
CREATE INDEX stop_times_pickup_type
  ON gtfs_stop_times
  USING btree
  (pickup_type );
CREATE INDEX stop_times_stop_id
  ON gtfs_stop_times
  USING btree
  (stop_id );
CREATE INDEX stop_times_stop_sequence
  ON gtfs_stop_times
  USING btree
  (stop_sequence );
CREATE INDEX stop_times_trip_id
  ON gtfs_stop_times
  USING btree
  (trip_id );
  
  
CREATE TABLE gtfs_stops
(
  stop_id integer NOT NULL,
  stop_code integer,
  stop_name character varying(255),
  stop_desc character varying(255),
  stop_lat numeric(10,8), -- TODO: check requested type-size.
  stop_lon numeric(10,8), -- TODO: check requested type-size.
  location_type boolean, -- Should be an Enum.
  parent_station integer, -- Should be an Enum.
  zone_id character varying(255),
  CONSTRAINT stops_pkey PRIMARY KEY (stop_id )
);
ALTER TABLE gtfs_stops
  OWNER TO obus;
CREATE INDEX stops_location_type
  ON gtfs_stops
  USING btree
  (location_type );
CREATE INDEX stops_parent_station
  ON gtfs_stops
  USING btree
  (parent_station );
CREATE INDEX stops_stop_lat
  ON gtfs_stops
  USING btree
  (stop_lat );
CREATE INDEX stops_stop_lon
  ON gtfs_stops
  USING btree
  (stop_lon );
CREATE INDEX stops_zone_id
  ON gtfs_stops
  USING btree
  (zone_id COLLATE pg_catalog."default" );


CREATE TABLE gtfs_shapes
(
  shape_id integer NOT NULL,
  shape_pt_sequence integer NOT NULL,
  shape_pt_lat numeric(8,6) NOT NULL,
  shape_pt_lon numeric(8,6) NOT NULL,
  CONSTRAINT shapes_pkey PRIMARY KEY (shape_id , shape_pt_sequence )
);
ALTER TABLE gtfs_shapes
OWNER TO obus;
