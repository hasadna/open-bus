## fetch_and_store_arrivals

siri.fetch_and_store_arrivals is a script that receives a list of bus stop codes, and retrieves data for these stops from SIRI. It can keep the results in file or in the database.

## How to run?

### Create a database
You need a postgres database with the correct schema. The schema file is available under siri/data/schema.sql

You need to do something like this:

      sudo -u postgres psql
      create database obus;
      \connect obus
      create role <USERNAME> with login password '<PASSWORD>';
      GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <USERNAME>;
      GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to <USERNAME>;
      
Exit the postgres shell (ctrl-D) and then import the schema:

     sudo -u postgres psql obus postgres < schema.sql
     

### Get the list of stop codes
Stop codes actually appear on bus stop signs. But if you want something more systematic you will have to find them in the GTFS. [See the GTFS documentation](https://github.com/hasadna/open-bus/blob/master/gtfs/working_with_GTFS.md). The script gtfs.parser.line_stops_finder might be helpful.

You need to create a CSV file, where the stop codes are in column with the title stop_code. Other columns will be ignored. See [stop_codes_sample.csv](https://github.com/hasadna/open-bus/blob/master/siri/data/stop_codes_sample.csv) for a minimal example. 
      
      
### create configuration file
Copy [siri/data/fetch_and_store_arrivals.config.example](https://github.com/hasadna/open-bus/blob/master/siri/data/fetch_and_store_arrivals.config.example) and make the changes you need. Make sure in particular that you supply siri user name, database user and password, and stops file name.

### Is open bus in PYTHON_PATH?
To be able to run the script from any current directory, make sure the project root folder is in the python path. 


### And... run!
This should now work:
  
       python3 -m siri.fetch_and_store_arrivals <your configuration file name>

      
