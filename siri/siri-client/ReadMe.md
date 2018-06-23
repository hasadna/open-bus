SIRI-Client is client application for manage SIRI requests and responses from Israel ministry of transportation (MOT). The main challenge that this application will deal with is that the correct protocol for collecting the geographic information of bus vehicles is SIRI-VM, but since this protocol is not available to the public by MOT this application will use the SIRI-SM protocol.

**1. Get GTFS**
SIRI-SM requests is based on GTFS information. This application will download the last version of the GTFS.

**2. Query GTFS**
Find GTFS schedules that you wish to find for them real time information.

**3. Define SIRI Queries**
Convert the GTFS schedules you found above to a SIRI query.

**4. Pack Queries into Request**
The user could define how many queries will be reside in one request and how often the query should be executed (for example: every minute for the next hour)

**5. Perform Requests**
The requests will execute in parallel

**6. Collect Responses**
Handle errors responses

**7. Validate Responses**
check that there is no duplicate responses.

**8. Push Data to Output**
user could define the output as a file, massage queue etc.

_Terms:_

SIRI-SM: Stop Monitoring service: Allows the exchange of the real-time arrivals and departures at a stop of public transport services.
SIRI-VM: Vehicle Monitoring service: Allows the exchange of the real-time positions of public transport vehicles.
GTFS - The General Transit Feed Specification defines a common format for public transportation schedules and associated geographic information.
