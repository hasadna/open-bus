# OpenBus Roadmap

## Project Mission and Summary
We use public data to improve public transport in Israel.  
Open Bus is a project of The Public Knowledge Workshop. 

## How to Get Involved
We welcome any kind of contribution. Look for [good first issue](https://github.com/hasadna/open-bus/labels/good%20first%20issue) and [help wanted](https://github.com/hasadna/open-bus/labels/help%20wanted) labeled issues, and make sure to read our [contributing guidlines](https://github.com/hasadna/open-bus/blob/master/CONTRIBUTING.md). 
Our [README](https://github.com/hasadna/open-bus/blob/master/README.md#want-to-help) has more info on getting started too.

## Goals for OpenBus
### Real-Delay - QoS Score
*Create a QoS (Quality-of-Service) score for public transport that can be viewed and sliced by agency, route, trip, stop, date and time.*  
*We wish to compare the planned trips to the actual trips (GTFS to SIRI). This information might help us discover problems such as trips that didn't happen, areas with bad traffic that buses usually are late for, etc.*  
	
### Accessibility Score
*Show how accessible are different locations and resources by public transport.*  
*We wish to measure accessibility between two areas, for example how many people that live in South Tel Aviv are connected to Kfar-Saba. And also to measure accessibility between area and some features like workplaces, universities, healthcare, culture etc. for example Many many people who live in Beer-Sheva are connected to workplaces?*  
-   Between Locations
-   Between Locations and Resources (jobs, leisure, health-care, nature, culture etc.)
-   Between Populations and Resources

### Complaints
*Work with 15-minutes on building a good complaint platform. Use complaints as a valuable data source.*  

### Website
*A suitable space to throw our stuff in and share them with the world.*

### Misc
-   Analyze cases of incentives given to private car owners. Such as company cars analysis [published by the MoF](http://mof.gov.il/chiefecon/economyandresearch/doclib/skiracalcalit_25062017.pdf). Parking is [another](https://www.themarker.com/opinion/1.5810354) [idea](https://www.globes.co.il/news/article.aspx?did=1001136685).
-   Get archive data from MOT (בקשות חופש מידע) and possibly from the agencies
-   Better future Open Data policies for transportation in Israel (work with תחבורה היום ומחר)
-   Better arrival time prediction

## Milestones
Short term - things we are working on now (but could always use help with)  
Medium term - things contributors can start working on that is not currently being worked on  
Long term - describe where our project is going (see Goals)  
**Sync this with the built-in github [milestones](https://help.github.com/articles/about-milestones/). Then every issue can be directly linked to a milestone upon creation**  

### Current Mission
Create a website that will display basic daily statistics for GTFS and SIRI.

### SIRI Archive
-   Country-wide continuous archiving of all buses.
-   Efficient query API
### GTFS Archive
-   Downloader that catches all MOT FTP file updates and archives them to S3
-   Archive daily GTFS statistics generated using from [GTFSTK](https://github.com/mrcagney/gtfstk)
-   Incremental Database Archive
### Real Delay
-   **Meta-QoS** - How good / bad is our SIRI data? Missing data, wrong data
-   As a first step - **compare stats on a route or stop level**, which is easier and might be good enough for some uses:
	-   Route stats - Trip counts, average total-trip time
	-   [Headway](https://en.wikipedia.org/wiki/Headway) - ([example](https://jasmcole.com/2015/03/02/two-come-along-at-once/))
-   **Align trips and compare per station**
	-   **Match SIRI trip to GTFS trip** -
		-   Our current method is using origin_aimed_departure_time, route and date ([source](https://github.com/hasadna/open-bus/blob/0fd5222b12a6062da7072972e89c4fc2e1aa47a0/postgres/adding_trip_id_to_siri_from_gtfs.sql#L44)). See [#24](https://github.com/hasadna/open-bus/issues/24).
		-   New trip_id field in SIRI?
		-   What are we missing? Test both (what about out-of-schedule trips?)
	-   **Diff the trips** -
		-   Define the measurements -    
			-   Actual arrival time at planned stops as compared to the schedule	    
			-   Departure - Yes / No → When?   
		-   Munge both data to a clean dataset for doing the stats    
			-   Infer arrival time at stop using the SIRI responses	    
			-   Loop lines issue - how big is it? See [#50](https://github.com/hasadna/open-bus/issues/50)
	-   **Aggregate and enable drilldown**
-   Handle changes over time. Choose between:
	-   Build an **Incremental GTFS** database we can query ([Google Doc](https://drive.google.com/drive/folders/0ByIrzj3OFMnIejRBVy04WjFLVFk))
	-   **Work directrly with GTFS files**, use them for stats every day, and when we need something historical we’ll just go over the files one by one.
	-   **Merge on insert with the most current GTFS data**
-   Fuse with complaint data.

### Accessibility
-   Resource and Location Datasets and API (OSM?)
	-   Get data for resources - OSM, CBS (למ”ס), Google, Municipal data
	-   Geo and Location data
		-   Choose meaningful locations
		-   How to set the borders and granularity? (GIS data…)
		-   Determine which lines or stops service each location
-   GTFS Only Accessibility ([POC](http://simplistic.me/urbanaccess-tel-aviv-demo.html))
-   Actual arrival times, depends on Real Delay progress
-   Future - compare to private car or other means of transportation

### Complaints
-   Automatically file a complaint to MOT and other Agencies
-   Complaint Analysis Platform - search, statistics, monitoring and alerting
-   Improve app and site data (formats, fields, tags, types)
-   Complaint Management - MVP
-   Fuse with GTFS and SIRI data
-   Improve app and site UX/UI (for GTFS/SIRI data fusion)
-   Scrape Social Media for more data
-   Complaint Management - CRM style
### Website
-   Blog
-   Slice and dice (obudget-style)
-   Map

## Specify Tasks
-   Goals → Milestones → Tasks → Issues  
Create an issue for each task. Take time to describe the task along with why you are doing this task. This will strengthen the vision for the project and help others get involved.

Tips for issues: Include as much context and help as possible! Add links, mention specific people involved by their username (i.e. @cjer). Articulate the problem or idea along with solutions and next steps.

Link to these issues in your Roadmap under each milestone.

## Be More Welcoming
-   Reorder git
    -   [https://opensource.guide/starting-a-project/](https://opensource.guide/starting-a-project/)
    -   [https://opensource.guide/building-community/](https://opensource.guide/building-community/)
    -   License
    -   Quick Start Guide / Tutorials
    -   Contributing Guidelines [#64](https://github.com/hasadna/open-bus/issues/64)
    -   Code of Conduct
    -   Maybe we need more than one repo? New ones for Complaints, Website and maybe Analysis work
-   Update issues
-   Rethink communication mediums - make it more open - currently googlegroup, whatsapp and github
-   Invite volunteers to present their work
-   Automate setup
