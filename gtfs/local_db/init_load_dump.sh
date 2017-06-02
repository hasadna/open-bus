#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE ROLE obus;
    CREATE DATABASE obus;
    GRANT ALL PRIVILEGES ON DATABASE obus TO obus;

EOSQL
pg_restore -h localhost -p 5432 -U postgres -d obus -v /docker-entrypoint-initdb.d/dump.dmp