# How to insert a GTFS file to PostGRES?

There are two ways to do it:
1) `postgres/insert_gtfs.sh` - a bash script that uses psql
2) `gtfs.parser.ps_insert` - a python module

The shell script is much (much much) faster, since it uses PostGRES `\copy` to insert directly from a CSV file. However
the `\copy` command is limited compared to what you can do with an Insert method, so the Python version can be
more flexible. 

## insert_gtfs.sh

`insert_gtfs.s`h receives three command line parameter: path to gtfs zip file, database user and database password.

Notes:

1. The script creates the tables itself, so no need to import the schema first. 

2. The script drops the current gtfs tables before creating the new ones. Any previous data in these tables will be
    lost. 

3. The script unzips the gtfs file to `/tmp/gtfs`. It will override any older files in this folder.

4. For most of the files, the script just inserts all the available fields. Two exceptions: the agency table,
   only two fields are inserted (id and name). In the stops file, it adds address & platform fields, calculated 
   from the stop description. 


### Extending GTFS
After running the insert script, you should

1. run `postgres/insert_route_stories.sh`
   The script creates the route stories, which are essentially a compressed version of stop times.
2. run `python3 -m gtfs.parser.nearest_station <config_file_name>`
   This script adds nearest_train_station and train_station_distance fields to the stops table.
   The script requires a configuration file with the fields `db_host`, `db_name`, `db_user` & `db_password`.


(simplifying shapes can be added at this point)

## ps_insert.py

1. ps_insert.py assume that the scema already exists, so you need to import the scema first.
   The schema file is gtfs/schema.sql. (Note that this isn't identical to the scema used by the shell script.)

2. Unzip the gtfs zip file somewhere. 

3. Copy the configuration file `conf/postgres_insert.config.example` and make the changes you need. 

4. To be able to run the script from any current directory, make sure open bus is in your `PYTHONPATH`.
   make sure the project root folder is in the python path.

5. Run: 

    `python3 -m gtfs.parser.ps_insert <your configuration file name>`




​       




