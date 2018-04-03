# OpenBus Roadmap
## Goals for OpenBus
TODO: divide goals to Short, Medium and Long term
### Real-Delay - QoS (Quality-of-Service) Score
*Create a QoS score for public transportation that can be viewed and sliced by agency, route, trip, stop, date and time.*
*Compare GTFS trips to SIRI trips,*
-   Compare stats (easier and might be good enough. route level):
	-   Trip counts
	-   Headway
-   Align trips and compare per station
	-   Match SIRI trip to GTFS trip - How?
		-   Our current method is using origin_aimed_departure_time, route and date ([source](https://github.com/hasadna/open-bus/blob/0fd5222b12a6062da7072972e89c4fc2e1aa47a0/postgres/adding_trip_id_to_siri_from_gtfs.sql#L44))
		-   New trip_id field in SIRI?
		-   What are we missing? Test both
	-   Compare / Diff the trips -
		-   Define the measurements -    
			-   Actual arrival time at planned stops as compared to the schedule	    
			-   Departure - Yes / No → When?   
		-   Munge both data to a clean dataset for doing the stats    
			-   Infer arrival time at stop using the SIRI responses	    
			-   Loop lines issue - how big is it?
		-   Aggregate and enable drilldown
-   How to handle changes over time -
	-   Try to build an incremental database we can query?    
	-   Or, work directrly with GTFS files, use them for stats every day, and when we need something historical we’ll just go over the files one by one.
-   Meta-QoS - How good / bad is SIRI?
-   Fuse with complaint data.
-   Questions
	-   What to do with out of schedule trips?
### Accessibility Score
*Show how accessible are different locations and resources by public transportation?*
-   This requires actual arrival times too
-   Between Locations -
	-   Choose meaningful locations
	-   How to set the borders and granularity? (GIS data…)
	-   Determine which lines or stops service each location
-   Between Locations and Resources
	-   Get data for resources - OSM, CBS (למ”ס), Google, Municipal data
	-   Initial example: [http://simplistic.me/urbanaccess-tel-aviv-demo.html](http://simplistic.me/urbanaccess-tel-aviv-demo.html)
-   Between Populations and Resources
-   Future - compare to private car or other means of transportation
### Complaints
*Work with 15-minutes on building a good complaint platform. Use the data for analysis.*
-   Complaint Analysis - search, statistics, monitoring and alerting
-   Fuse with GTFS and SIRI data
-   Complaint Management - CRM style
-   Automatic Filing to MOT and other Agencies
-   Improve app and site UX/UI and data
-   Scrape Social Media for more data
### Website
*A suitable space to throw our stuff in*
-   Slice and dice
-   Map
-   Blog
### Misc
-   Analyze Incentives for using private car (public & private sector)
-   Get archive data from MOT (בקשות חופש מידע) and possibly from the agencies
-   Better future Open Data for Transportation (תחבורה היום ומחר)
-   Better arrival time prediction
## Specify Tasks
-   Goals → Tasks → Issues
## Be More Welcoming
-   Reorder git
	-   [https://opensource.guide/starting-a-project/](https://opensource.guide/starting-a-project/)
    -   [https://opensource.guide/building-community/](https://opensource.guide/building-community/)
    -   License
    -   Quick Start Guide / Tutorials
    -   Contributing Guidelines [#64](https://github.com/hasadna/open-bus/issues/64)
    -   Code of Conduct
    -   Maybe we need more than one repo?  
-   Update issues
-   Rethink communication mediums - make it more open - currently googlegroup, whatsapp and github
-   Invite volunteers to present their work
-   Automate setup
