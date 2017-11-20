#!/bin/bash

#This script will be used temporary for uploading daily the gtfs and updating siri data

if [ "$#" -ne 2 ]; then
    echo "Usage: update_daily_siri_data.sh db_username db_password"
    exit -1
fi

export PGPASSWORD=$2

day="$(date --date='1 days ago' +'%d')"
month="$(date --date='1 days ago' +'%m')"
year="$(date --date='1 days ago' +'%Y')"
fullDate=$year-$month-$day
echo updating for date: $fullDate

gtfs_file='/tmp/gtfs_'$year'-'$month'-'$day'.zip'
aws s3 cp s3://s3.obus.hasadna.org.il/$year-$month-$day.zip $gtfs_file

PATH=$HOME/open-bus/postgres:$PATH
cd $HOME/open-bus/postgres

insert_gtfs.sh $gtfs_file $1 $2 $full_date
rm $gtfs_file
echo uploaded gtfs file

psql -h 127.0.0.1 -U $1 -d obus -f add_gtfs_shape_dist_ratio.sql
echo added gtfs_shape_dist_ratio

psql -h 127.0.0.1 -U $1 -d obus -f create_gtfs_shape_lines_table.sql
echo created gtfs_shape_lines

psql -h 127.0.0.1 -U $1 -d obus -v v1=$day -v v2=$month -v v3=$year -f adding_trip_id_to_siri_from_gtfs.sql
echo added trip id

psql -h 127.0.0.1 -U $1 -d obus -v v1=$day -v v2=$month -v v3=$year -f add_route_offset.sql
echo added route offset

#add here script when bus arrived
