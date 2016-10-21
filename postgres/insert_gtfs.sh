#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: insert_gtfs.sh  gtfs_file db_username db_password"
    exit -1
fi

export PGPASSWORD=$3

mkdir /tmp/gtfs

time unzip -o -d /tmp/gtfs $1

cut -d',' -f1,2 /tmp/gtfs/agency.txt  > /tmp/gtfs/agency_for_db.txt
python3 preprocess_stops_for_insert.py /tmp/gtfs/stops.txt /tmp/gtfs/stops_for_db.txt

time psql -h 127.0.0.1 -U $2 obus < insert_gtfs.sql

