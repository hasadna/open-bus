# TODO: Validate index-creation syntax.
# TODO: Deside which indexes are wanted.
# TODO: Create enums for relevant fields (inline comments).
# TODO: Make sure type-sizes are fine.
# TODO: Consider using TinyInt instead of INT when relevant.
# TODO: Check requested type-size for coordinates.
# TODO: Check requested type-size for shape_dist_traveled.


CREATE TABLE agency(
    agency_id INT(8) NOT NULL PRIMARY KEY,
    agency_name VARCHAR(100) NOT NULL,
    agency_url VARCHAR(100) NOT NULL,
);

CREATE TABLE routes (
    route_id INT(32) NOT NULL PRIMARY KEY,
    agency_id INT(8),
    route_short_name VARCHAR(50) NOT NULL,
    route_long_name VARCHAR(255) NOT NULL,
    route_desc VARCHAR(10),
    route_type INT(4) NOT NULL, # Should be an Enum.
    route_color VARCHAR(9), # Can be an Enum.
    KEY `agency_id` (agency_id),
    KEY `route_type` (route_type)
);

CREATE TABLE trips (
    trip_id INT(128) NOT NULL PRIMARY KEY,
    route_id INT(32) NOT NULL,
    service_id INT(32) NOT NULL,
    direction_id INT(4),
    shape_id INT(32),
    KEY `route_id` (route_id),
    KEY `service_id` (service_id),
    KEY `direction_id` (direction_id),
    KEY `shape_id` (shape_id)
);

CREATE TABLE calendar (
    service_id INT(32) NOT NULL PRIMARY KEY,
    sunday BOOLEAN NOT NULL,
    monday BOOLEAN NOT NULL,
    tuesday BOOLEAN NOT NULL,
    wednesday BOOLEAN NOT NULL,
    thursday BOOLEAN NOT NULL,
    friday BOOLEAN NOT NULL,
    saturday BOOLEAN NOT NULL,
    start_date VARCHAR(8) NOT NULL,	
    end_date VARCHAR(8) NOT NULL,
    KEY `service_id` (service_id)
);

CREATE TABLE stop_times (
    id INT(12) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    trip_id INT(128) NOT NULL,
    arrival_time VARCHAR(8) NOT NULL,
    departure_time VARCHAR(8) NOT NULL,
    stop_id INT(32) NOT NULL,
    stop_sequence INT(8) NOT NULL,
    pickup_type BOOLEAN,
    drop_off_type BOOLEAN,
    shape_dist_traveled INT(32),
    KEY `trip_id` (trip_id),
    KEY `stop_id` (stop_id),
    KEY `stop_sequence` (stop_sequence),
    KEY `pickup_type` (pickup_type),
    KEY `drop_off_type` (drop_off_type)
);

CREATE TABLE stops (
    stop_id INT(32) NOT NULL PRIMARY KEY,
    stop_code INT(32),
    stop_name VARCHAR(255) NOT NULL,
    stop_desc VARCHAR(255),
    stop_lat DECIMAL(10,20) NOT NULL, # TODO: check requested type-size.
    stop_lon DECIMAL(10,20) NOT NULL, # TODO: check requested type-size.
    location_type BOOLEAN, # Should be an Enum.
    parent_station INT(2), # Should be an Enum.
    zone_id VARCHAR(255),
    KEY `zone_id` (zone_id),
    KEY `stop_lat` (stop_lat),
    KEY `stop_lon` (stop_lon),
    KEY `location_type` (location_type),
    KEY `parent_station` (parent_station)
);

CREATE TABLE shapes (
    shape_id INT(32) NOT NULL PRIMARY KEY,
    shape_pt_sequence INT(8) NOT NULL PRIMARY KEY,
    shape_pt_lat DECIMAL(8,6) NOT NULL,
    shape_pt_lon DECIMAL(8,6) NOT NULL,
    shape_dist_traveled INT(64) # TODO: check requested type-size.
);