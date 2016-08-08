#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE ROLE openbus;
    CREATE DATABASE gtfs;
    GRANT ALL PRIVILEGES ON DATABASE gtfs TO openbus;
EOSQL

psql -v ON_ERROR_STOP=1 --username "postgres" gtfs < /docker-entrypoint-initdb.d/schema.txt
