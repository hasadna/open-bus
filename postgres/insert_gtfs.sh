#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: insert_gtfs.sh  gtfs_file db_username db_password gtfs_date"
    exit -1
fi

export PGPASSWORD=$3

if [ ! -f $1 ]; then
    echo "File not found. Aborting."
    exit -1
fi

day="$(date -d $4 +'%d')"
month="$(date -d $4 +'%m')"
year="$(date -d $4 +'%Y')"

mkdir -p /tmp/gtfs

time unzip -o -d /tmp/gtfs $1

cut -d',' -f1,2 /tmp/gtfs/agency.txt  > /tmp/gtfs/agency_for_db.txt

time psql -h 127.0.0.1 -U $2 obus -v v1=$year -v v2=$month -v v3=$day < insert_gtfs.sql

