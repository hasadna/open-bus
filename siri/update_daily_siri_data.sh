#!/bin/bash

#This script will be used temporary for uploading daily the gtfs and updating siri_real_time_arrivals table (our evaluation of the arrival time).
# NOTE - this script doesn't query siri! To make siri request use fetch_and_store_arrivals.py and see working_with_SIRI.md
# updaing gtfs is done using the insert_gtfs.sh script.
# updating the siri_real_time_arrivals is based on the analyseRealTime/Main.py code. 
# analyseRealTime/Main.py relies on existence of:   
# 1. trip id on each siri entry in the siri_arrivals table (this is not something we get automatically and is done using the adding_trip_id_to_siri_from_gtfs.sql)
# 2. route offset on each siri entry - done using add_route_offset.sql
# The trip id to siri entry matching can be done only after adding the following data:
# 1. add_gtfs_shape_dist_ratio.sql - add to gtfs_stop_times the ratio of the travel distance.
# 2. create_gtfs_shape_lines_table.sql - turns shape table entries into postgis shapes.


if [ "$#" -ne 4 ]; then
    echo "Usage: update_daily_siri_data.sh db_username db_password aws_bucket analysis_config"
    exit -1
fi

export PGPASSWORD=$2

day="$(date --date='1 days ago' +'%d')"
month="$(date --date='1 days ago' +'%m')"
year="$(date --date='1 days ago' +'%Y')"
fullDate=$year-$month-$day
echo updating for date: $fullDate

gtfs_file='/tmp/gtfs_'$year'-'$month'-'$day'.zip'
aws s3 cp $3/$year-$month-$day.zip $gtfs_file

PATH=$HOME/open-bus/postgres:$PATH
cd $HOME/open-bus/postgres

insert_gtfs.sh $gtfs_file $1 $2 $fullDate
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

python3 $HOME/open-bus/siri/analyseRealTime/Main.py -c $3 -d $fullDate
echo calculated estimated arrival time
