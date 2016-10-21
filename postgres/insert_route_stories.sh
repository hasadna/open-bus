#!/bin/bash

# Script for adding route stories data to gtfs in postgres
# Runs route story generation, and then adds the results to the db
# The script assumes the gtfs is already in database, probably inserted using insert_gtfs.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 db_username db_password"
    exit -1
fi

# Create configuration file for the route_stories script

CONFIG_FILE_NAME=/tmp/gtfs/make_route_stories.config
echo "" > $CONFIG_FILE_NAME
echo "source = db" >> $CONFIG_FILE_NAME
echo "db_host = localhost" >> $CONFIG_FILE_NAME
echo "db_name = obus" >> $CONFIG_FILE_NAME
echo "db_user = $1" >> $CONFIG_FILE_NAME
echo "db_password = $2" >> $CONFIG_FILE_NAME
echo "output_folder = /tmp/gtfs" >> $CONFIG_FILE_NAME
echo >>  $CONFIG_FILE_NAME


# Run route stories generation
python3 -m gtfs.parser.route_stories $CONFIG_FILE_NAME

export PGPASSWORD=$2

# run route story insert
time psql -h 127.0.0.1 -U $2 obus < insert_route_stories.sql



