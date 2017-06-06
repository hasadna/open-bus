#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE ROLE obus;
    CREATE DATABASE obus;
    GRANT ALL PRIVILEGES ON DATABASE obus TO obus;
    ALTER ROLE obus WITH LOGIN;

EOSQL
pg_restore -h localhost -p 5432 -U postgres -d obus -t gtfs_calendar -t gtfs_routes -t gtfs_shapes -t gtfs_stop_times -t gtfs_stops -t gtfs_trips -t route_story_stops -t siri_arrivals_filtered -t siri_raw_responses -t station_walking_distance -t train_passenger_counts -t train_passengers_per_hour -t train_station_exits -v /docker-entrypoint-initdb.d/dump.dmp
