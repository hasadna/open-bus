# OPEN BUS IN CIVICHACK 2019
Do you also think that SOMEONE must improve the public transportation in Israel?   
Well, we have all real-time bus data in Israel from the past months for you to start doing it!   
Our main challenge is to develop automatic tools to validate the data accuracy and to detect anomalies in bus trips. All for the purpose of creating a data-based report about the actual public transportation status in Israel, and bring the future!   

## Who Are We?
**[Open Bus](https://github.com/hasadna/open-bus)** is a team of [The Public Knowledge Workshop](https://www.hasadna.org.il/). We use public data to improve public transport in Israel.   
We currently work on one main project, **Real Delays**, aggregating real-time bus data and comparing it to the planned schedules.

## Data Overview
We get our data from the Israeli ministry of transport.  We have two main types of data:
1. Planned routes and schedules: [GTFS](https://www.gov.il/he/departments/general/gtfs_general_transit_feed_specifications) files that we download on a daily basis. 
2. Real time GPS data: Buses GPS data that bus agencies provide in real time to the ministry of transport. We built a service that collects the data on real time using [SIRI SM](https://www.gov.il/he/Departments/General/real_time_information_siri) protocol, and saves it to our servers. 

## Challenges
1. **:trophy: Data Science :trophy: Identify bus line by its actual driven route :trophy:** https://github.com/hasadna/open-bus/issues/156
2. **:trophy: Data Science :trophy: Anomaly detection in bus trips :trophy:** https://github.com/hasadna/open-bus/issues/155
3. **:trophy: Fullstack :trophy: Interactive map for investigating bus trips using real-time and schedule data :trophy:** https://github.com/hasadna/open-bus/issues/151

