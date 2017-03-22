## fetch_and_store_arrivals

siri.fetch_and_store_arrivals is a script that receives a list of bus stop codes, and retrieves data for these stops from SIRI. It can keep the results in file or in the database.

## How to run?

### Create a database tables
You need a postgres database with the correct schema. The schema file is available under siri/data/schema.sql

### Get the list of stop codes
Stop codes actually appear on bus stop signs. But if you want something more systematic you will have to find them in the GTFS. [See the GTFS documentation](https://github.com/hasadna/open-bus/blob/master/doc/working_with_GTFS.md). The script gtfs.parser.line_stops_finder might be helpful.

You need to create a CSV file, where the stop codes are in column with the title stop_code. Other columns will be ignored. Something like that should work:

```
stop_code
90
103
137
```

​      

### create configuration file
Copy [conf/fetch_and_store_arrivals.config.example](https://github.com/hasadna/open-bus/blob/master/conf/fetch_and_store_arrivals.config.example) and make the changes you need. Make sure in particular that you supply siri user name, database user and password, and stops file name.

### Is open bus in PYTHON_PATH?
To be able to run the script from any current directory, make sure the project root folder is in the python path. 


### And... run!
This should now work:

       python3 -m siri.fetch_and_store_arrivals <your configuration file name>

## Running with crontab

- Create a script for running fetch and store with your configuration, something like:
  ```bash
  #! /bin/bash

  export PYTHONPATH=/path/to/repository/open-bus

  python3 -m siri.fetch_and_store_arrivals /path/to/config/fetch_and_store_arrivals.config

  ```
- Test your work by running the script. 

- Add the script to crontab. Run `crontab -e` and add something like (read crontab doc to understand!)

  ```
  */2 5-23,0-1 * * 7,1-5 /path/tp/script/fetch_and_store.sh >& /tmp/fetch_arrivals.log
  ```