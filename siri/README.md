# SIRI project in Hasadna/open-bus

The SIRI project of open-bus has the following goals:

1. retrieve from MOT all available SIRI data, about all the bus routes, all the time
2. save the data in a usable format, for indefinite time.
3. Enable accessing this data and use it for all kinds of applications


## Technical Overview

This project includes 2 processes: 

1. siri-retriever 
2. gtfs-reader

the 2 projects communicate between them - through HTTP REST, and through the (shared) file system.

Currently (May 2019) the 2 processes run on the same machine - A DigitalOcean cloud machine - OS Ubuntu.

A detailed description of each process is available below.

Both processes are developed in the JAVA language. Source code is open-source, can be seen [here](https://github.com/hasadna/open-bus/tree/master/siri).

## Functional View
### gtfs-reader
The gtfs-reader process reads **every** night the (updated) GTFS file from Ministry of Transportation.
(note that this is not connected in any way to another process in the open-bus project, that reads GTFS files and archives them. The GTFS files retrieved by our gtfs-reader are used by gtfs-reader to create some files, and then they are discarded).

gtfs-reader creates (from data in the GTFS files) several "schedule files". These files are then passed to siri-retriever (Exact technical details about how this is done, are available below)

gtfs-reader process is up all the time. It actually performs some work only once a day, usually at 3:00 AM (at night).

### siri-retriever
The siri-retriever process sends queries to the **MOT-SIRI-server** and receives replies that carry the SIRI data. siri-retriever writes all that data to a storage of raw data. this storage of raw data is considered "the source of truth" - we archive this data forever, and it can be accessed when needed.

The SIRI "raw data" that we collect is then used by several other applications that process SIRI data.

siri-retriever works constantly. It retrieves SIRI data about all bus routes in Israel, and all bus vehicles in each route.
siri-retriever queries each route once a minute (this is the current interval, it could be changed if needed. See below about how this interval was decided). When querying a route, siri-retriever receives data about all bus vehicles that are currently moving along the route! As a result, we gather the locations of ALL moving buses in Israel, once a minute.

siri-retriever uses several non-trivial algorithms to generate the queries to MOT-SIRI-server in a way that will result with data about bus locations along each route (more details below).

siri-retriever uses the "schedule files" created by gtfs-reader, in order to construct queries only for active routes. We do not query all routes all the time. Only the routes that operate at each point in time.


## Data View
