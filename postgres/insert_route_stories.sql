-- run timing to see how much time everything takes
\timing


-- drop old tables
DROP TABLE IF EXISTS route_story_stops;
DROP TABLE IF EXISTS trip_route_story;

\echo ********** importing route story stops **********


CREATE TABLE route_story_stops
(
  route_story_id      INTEGER,
  arrival_offset        INTEGER,
  departure_offset      INTEGER,
  stop_id             INTEGER,
  stop_sequence       INTEGER,
  pickup_type         BOOLEAN,
  drop_off_type       BOOLEAN
);


\copy route_story_stops from '/tmp/gtfs/route_stories.txt' DELIMITER ',' CSV HEADER;

CREATE INDEX route_story_stops_route_story_id
  ON route_story_stops USING BTREE (route_story_id);

CREATE INDEX route_story_stops_stop_id
  ON route_story_stops USING BTREE (stop_id);


\echo ********** importing trip route stories **********
CREATE TABLE trip_route_story
(
  trip_id      CHARACTER VARYING(50) NOT NULL,
  arrival_time        CHARACTER VARYING(8),
  route_story_id      INTEGER
);

\copy trip_route_story from '/tmp/gtfs/trip_to_stories.txt' DELIMITER ',' CSV HEADER;

ALTER TABLE trip_route_story
  ADD CONSTRAINT trip_id_pkey PRIMARY KEY (trip_id);

ALTER TABLE route_story_stops OWNER TO obus;
ALTER TABLE trip_route_story OWNER TO obus;

-- make sure re:dash can access the new tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO redash;