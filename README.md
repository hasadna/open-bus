# Open Bus
[![Build Status](https://travis-ci.org/hasadna/open-bus.svg?branch=master)](https://travis-ci.org/hasadna/open-bus)
[![codecov](https://codecov.io/gh/hasadna/open-bus/branch/master/graph/badge.svg)](https://codecov.io/gh/hasadna/open-bus)

Open Bus is a project of [The Public Knowledge Workshop](http://www.hasadna.org.il).

We use public data to improve bus service - and public transport in general - in Israel.

We're currently working on one main project, **Real Delays**, aggregating real-time bus data and comparing it to the planned bus schedules.

## Where does the data come from?

1. Planned (static) data: The Ministry of Transport publishes a file called GTFS. This file contains planned trips data for the next 60 days. Alongside it, in the same FTP folder, there are a number of files with additional related data. 
2. Online data: the MoT has a webservice that provides real-time data. The webservice is called [SIRI SM] (https://github.com/hasadna/open-bus/wiki/Bus-Real-Time-(SIRI)-Data-Documentation).

## Want to help?
The project is currently focused on aggregating and analyzing data, so we need mainly Python developers and data scientists. We also have side tasks that are quite "stand-alone".

We are using Python 3 for all of our analysis, GTFS and "ETL" code, Java for the siri fetching code.

To get started, check [our wiki](https://github.com/hasadna/open-bus/wiki) and have a look at [our task board](https://github.com/hasadna/open-bus/projects/3) to see what we're working on

We recommend contacting us by [filling up the workshop's new volunteer form](https://docs.google.com/forms/d/e/1FAIpQLSdfAeyMNV3GOsHLIR4FLcb0D7YelNt69W4Aq2UAYF9O5eYzhw/viewform?c=0&w=1). There's sometimes, but not always, someone working on the project in the Public Knowledge Workshop Tel-Aviv development meetings (Monday evenings).
