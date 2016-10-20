## inserting into postgres db

## How to run?

### Create a database
You need a postgres database with the correct schema. The schema file is available under gtfs/schema.sql

You need to do something like this:

      sudo -u postgres psql
      create database obus;
      \connect obus
      create role <USERNAME> with login password '<PASSWORD>';
      GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <USERNAME>;
      GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to <USERNAME>;

Exit the postgres shell (ctrl-D) and then import the schema:

     sudo -u postgres psql obus postgres < schema.sql



### create configuration file
Copy [gtfs/data/postgres_insert.config.example] and make the changes you need.

### Is open bus in PYTHON_PATH?
To be able to run the script from any current directory, make sure the project root folder is in the python path.


### And... run!
This should now work:

       python3 -m gtfs.parser.ps_insert <your configuration file name>


