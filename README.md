# Open Bus

Open Bus is a project of [The Public Knowledge Workshop](http://www.hasadna.org.il). 

We use public data to improve bus service - and public transport in general - in Israel.

We currently work on one main project, **Real Delays**, aggregating real-time bus data and comparing it to the planned bus schedules.

## Where does the data come from?

1. Planned (static) data: The Ministry of Transport publishes a file called GTFS. This file contains planned trips data for the next 60 days. [Start here for information](https://github.com/hasadna/open-bus/blob/master/doc/working_with_GTFS.md) about GTFS and what we do with it. The [gtfs](https://github.com/hasadna/open-bus/tree/master/gtfs) package is where we work on code for reading GTFS, parsing and loading it to DB. 
2. Online data: the MoT has a webservice that provides real-time data. The webservice is called SIRI SM. [Start here for information](https://github.com/hasadna/open-bus/blob/master/doc/working_with_SIRI.md) about the protocol. The [siri](https://github.com/hasadna/open-bus/tree/master/siri) package has code for accessing SIRI. To understand what's going on, start at [siri/fetch_and_store_arrivals.py](https://github.com/hasadna/open-bus/blob/master/siri/fetch_and_store_arrivals.py).

Some Jupyter Notebook examples for working directtly with GTFS - [Blog posts](http://simplistic.me/tag/gtfs.html) / [github](https://github.com/cjer/cjer-pelican/tree/master/content/notebooks)

## Want to help?
The project is currently focused on aggregating and analysing data, so we need mainly Python developers and data scientists. We also have side tasks that are quite "stand-alone".

We are using Python 3.5.x . Some of the code requires Postgres SQL, and we are moving to use PostGIS.

To get started, clone the repository, and have a look at [our issues](https://github.com/hasadna/open-bus/issues) and [the doc directory](https://github.com/hasadna/open-bus/blob/master/doc/), to see what we need help with. You are welcome to check out our new (and still not perfect) [ROADMAP](https://github.com/hasadna/open-bus/blob/master/ROADMAP.md) too.

We recommend contacting us by [filling up the workshop's new volunteer form](https://docs.google.com/forms/d/e/1FAIpQLSdfAeyMNV3GOsHLIR4FLcb0D7YelNt69W4Aq2UAYF9O5eYzhw/viewform?c=0&w=1). There's sometimes, but not always, someone working on the project in the Public Knowledge Workshop Tel-Aviv development meetings (Monday evenings).
