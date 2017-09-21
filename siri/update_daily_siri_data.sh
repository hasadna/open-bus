#!/bin/bash


if [ "$#" -ne 2 ]; then
    echo "Usage: update_daily_siri_data.sh db_username db_password"
    exit -1
fi

export PGPASSWORD=$2

day="$(date +'%d')"
month="$(date +'%m')"
year="$(date +'%Y')"

echo updating for date: $day'-'$month'-'$year

psql -h 127.0.0.1 -U $1 -d obus -v v1=$day -v v2=$month -v v3=$year -f ../postgres/adding_trip_id_to_siri_from_gtfs.sql
echo added trip id

psql -h 127.0.0.1 -U $1 -d obus -v v1=$day -v v2=$month -v v3=$year -f ../postgres/add_route_offset.sql
echo added route offset