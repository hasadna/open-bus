# Open Bus

Open Bus is a project of [The Public Knowledge Workshop](http://www.hasadna.org.il). 

We use public data to improve bus service - and public transport in general - in Israel.

We currently work on two sub-projects: 

1. Real Delays: Aggregating real-time bus data and comparing it to the planned bus schedules. 
2. Bus2Train: Analyze bus service to and from train stations.


## Where does the data come from?

1. Planned (static) data: The Ministry of Transport publishes a file containing planned trips data for the next 60 days. [Read this file](https://github.com/hasadna/open-bus/blob/master/doc/working_with_GTFS.md) for more information about GTFS and what we do with it. The [gtfs](https://github.com/hasadna/open-bus/tree/master/gtfs) package is where we work on code for reading GTFS, parsing and loading it to DB. 
2. Online data: the MoT has a webservice that provides real-time data. The webservice is called SIRI SM. [See here](http://he.mot.gov.il/index.php?option=com_content&view=article&id=2243:pub-trn-memchakim&catid=167:pub-trn-dev-info&Itemid=304) for information about it from the ministry of transport. The [siri](https://github.com/hasadna/open-bus/tree/master/siri) package has code for accessing SIRI. To understand what's going on, start at [siri/fetch_and_store_arrivals.py](https://github.com/hasadna/open-bus/blob/master/siri/fetch_and_store_arrivals.py).


## Want to help?
Both of our sub-projects are currently about aggregating and analysing data, so we need mainly Python developers and data scientists. We also have side tasks that are quite "stand-alone" and are suitable for people stating up. 

We are using Python 3.5.x . Some of the code requires Postgres SQL. 

To get started, clone the repository, and have a look at [our issues](https://github.com/hasadna/open-bus/issues) to see what we need help with. 
