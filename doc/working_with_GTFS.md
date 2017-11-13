
What's in the GTFS
------------------

GTFS is the format used by the Ministry of Transport to publish planned public transport trips data. It's a set of data tables, published in csv files, and compressed together in a zip file. 

The data in the GTFS includes:

* list of public transport routes (lines) - routes table
* list of bus stops and train stations - stops table
* list of trips (rides) - when buses travel and where they call - trips, calendar and stop_times tables 
* geographic coordinates of bus trips, can be used to draw them on the map - shapes table 

[This entity relations diagram](https://github.com/hasadna/open-bus/blob/master/doc/gtfs_src_entity_diagram.png) can help you understand the relationships between the tables. For more information read the specification on the [MoT website](http://he.mot.gov.il/index.php?option=com_content&view=article&id=2244:pub-trn-gtfs&catid=167:pub-trn-dev-info&Itemid=304), and also [Google's Developers Website](https://developers.google.com/transit/gtfs/reference/).

*Note: the MoT, as public transport regulator, sets the schedule of departures for each bus line (the times when it should leave the first stop). The times in the GTFS for other stops do not bind the operators. There's probably no effort to make sensible estimates of when buses will arrive to each stop.*

The GTFS is published nightly, and archived by the [Open Train project](http://gtfs.otrain.org/static/archive/). 

### GTFS in our DB

We have a script that imports a GTFS file to PostgreSQL.  See [Inserting_GTFS_to_PostGRES.md](Inserting_GTFS_to_PostGRES.md) for information on how to use it.  

Once the data is in the DB, [here are examples](useful_GTFS_queries.md) for some queries you can run. 

You can use the [Open Budget's re:dash instance](http://data.obudget.org) to access our database, including the GTFS table. 

To find out what date the GTFS was uploded check out the `gtfs_update_history` table.

gtfs_reader
-----------

The `gtfs.parser.gtfs_reader` module can be used to read GTFS data to memory. To do this, you create a GTFS object:

     import gtfs.parser.gtfs_reader
     g = GTFS('gtfs/sample/israel-public-transportation.zip')

*Note: The sample [/data/sample/israel-public-transportation.zip](https://github.com/hasadna/open-bus/tree/master/data/sample) has all the GTFS data for only 10 bus routes. It can be used for testing when you don't want to load a full GTFS file.*

The GTFS object contains dictionaries. One dictionary for each of the following GTFS tables: `agencies`, `routes`, `shapes`, `services` (calendar table), `trips`, and `stops`. 

Because loading data might be time consuming, creating a GTFS object doesn't actually load any data. You need to call one or more of the load functions to actually read the data from the file. 

     g.load_agencies()
     g.load_routes()
     g.load_shapes()
     g.load_services()
     g.load_trips()
     g.load_stops()

Or you can `load_all` to load everything (but you probably don't want to).

      g.load_all()

The exception is the `stop_times` table. There's no stop_times dictionary in the GTFS object. Calling `g.load_stop_times()` will populate the `stop_times` field in the `trip` objects. 


Route stories
-------------
Route stories are described in details in the [docstring of the module that computes them](https://github.com/hasadna/open-bus/blob/master/gtfs/parser/route_stories.py). The tl;dr is that they are a way to compress the `stop_times` table. 

Route stories can be created from the GTFS DB or from the original GTFS zip file. To run it on database, it's best to use `postgres/insert_route_stories.sh`. 

To run it directly: 

```shell
python -m gtfs.parser.route_stories <config_file_name>
```
Once you created the route stories, you can read them from your code:

```python
from gtfs.parser.route_stories import load_route_stories_from_csv
route_stories, trip_to_route_stories = load_route_stories_from_csv('gtfs/sample/route_stories.txt', 'gtfs/sample/trip_to_stories.txt')
```


Where does my line call?
------------------------
If you have a line number, you can get a list of the stops where it calls. 

     python -m gtfs.parser.line_stops_finder --line_number 189 --gtfs_folder gtfs/sample --output_file stops_for_189.txt
The output file will include stop id, stop code, stop name and town. 

This script uses route stories, so you must generate route stories before running it (see above).

The script is interactive. It will show you all the lines with the given line number, and ask you to choose which one you want. Also, if the line calls in different stops in different dates, it will ask you to choose which dates you want. 


Other random information
-------------------------
* `stop_id` vs. `stop_code`:  
  * Stops table contains two fields that look similar, stop_id and stop_code. stop_code is the actual number of the stop in the MoT systems. It appears on the physical signage at the bus stop. It is also the number that should be used for SIRI queries. stop_id is just an internal key inside the GTFS, referenced in the stop_times table.  
  * However - stop_code isn't unique - central stations have one stop_code, and all different platforms / floors in them will share the same stop_code. 
* `trip_id`: Trip ids are composed of two parts, separated by underscore (e.g.: `337972_020117`). The first part is (probably) an internal ID used in the MoT systems. It is stable (so if the trip stops for a few days and resumes, it will have the same first part). The second part is the start date of the trip, identical to the `start_date` field in the matching service. This means that trips `337972_020117`  in the file for 2017-01-02 is probably the same trip as `337972_030117` in the file for 2017-01-03. 
* pickup_type & drop_off_type in stop_times table (and route stories): the values of these fields are a bit confusing. If pickup_type == 0, then pickup is available. If pickup_type == 1, no pickup is available (so it's a drop off station only). Same goes for drop_off_type. The DB import script changes the column name so they make more sense. 
