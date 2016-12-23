# SIRI SM

SIRI SM is a request-reply web service.

The format of all the timestamp is full ISO 8601, e.g. `2012-10-31T09:39:39.480+02:00`.

## Resources

- This document is based on the [documentation published by MoT](http://he.mot.gov.il/index.php?option=com_content&view=article&id=2243:pub-trn-memchakim&catid=167:pub-trn-dev-info&Itemid=304). 
- There's a [request-reply example](http://media.mot.gov.il/PDF/HE_TRAFFIC_PUBLIC/ANHAYIOT/Request-Response.zip) on the MOT website. But it's not comprehensive - fields that are often included in replies are missing.
- See also the following two examples in our doc folder:
  - [reply_example_1.xml](/doc/reply_example_1.xml) a more comprehensive example extracted using fetch_and_store_arrivals.py
  - [reply_example_2.xml](/docs/reply_example_2.xml) a reply generated at night time and shows some error messages

## Our Code

the `siri` package contains the code for connecting to the service, retrieving data, parsing it and writing to the db. It has the following modules:

- `arrivals.py` - send request and receive response from the service
- `siri_parser.py` - parse the response xml 
- `db.py` - write the response to PostGRES. We use two tables:
  - siri_raw_response - the XML received from the service
  - siri_arrivals - parsed data from all the [Monitored Stop Visit] xml entities (see below).
- `fetch_and_store_arrivals.py` - a script that uses the three other modules to fetch and store data on a given list of stops.

## Protocol: requests

The request is called `Stop Monitoring Request`. It's a request for information on the next arrivals to a given stop. Each request is for one stop (*or one pre-define set of stops, I don't know what that means). Several stop monitoring requests can be sent together in one `Service Request`.

### Service Request

Fields: 

- RequestTimestamp 
- RequestorRef - user name received from MoT when registering. The Public Knowledge Workshop has two user names (for open train and open bus).
- MessageIdentifier (Optional) - The reply will contain the same identifier, so they can be paired up if necessary.

Example:

```xml
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:acsb="http://www.ifopt.org.uk/acsb" xmlns:datex2="http://datex2.eu/schema/1_0/1_0" xmlns:ifopt="http://www.ifopt.org.uk/ifopt" xmlns:siri="http://www.siri.org.uk/siri" xmlns:siriWS="http://new.webservice.namespace" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="./siri">
  <SOAP-ENV:Header />
  <SOAP-ENV:Body>
      <siriWS:GetStopMonitoringService>
          <Request xsi:type="siri:ServiceRequestStructure">
              <siri:RequestTimestamp>2012-10-31T09:39:39.480+02:00</siri:RequestTimestamp>
              <siri:RequestorRef xsi:type="siri:ParticipantRefStructure">KLM12345</siri:RequestorRef>
              <siri:MessageIdentifier xsi:type="siri:MessageQualifierStructure">0100700:1351669188:4684</siri:MessageIdentifier>
             .... 1 or more stop monitoring requests come here ...
           </Request>
      </siriWS:GetStopMonitoringService>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
```



### Stop Monitoring Request 

fields: 

- Version - SIRI version. Current MoT production version is IL2.7 (11/2016). **It's important to use 2.7 rather than earlier versions to get the Vehicle Location field**
- RequestTimestamp 
- MessageIdentifier (optional) -The reply will contain the same identifier, so they can be paired up if necessary.
- Preview-Interval (optional) - ??, default 30 minutes
- StartTime (optional) - ??, default current time
- MonitoringRef - stop code for querying. stop_code values can be found in GTFS stops table (remember to use stop_code, not stop_id)
- LineRef (optional) - specific line to query at the given stop. By default result will be returned for all lines calling in the stop. The value should be route_id from the GTFS routes table.
- Language (optional) - default is Hebrew
- Maximum-StopVisits (optional) - cap the number of future buses that will be returned. Default is 10.
- MinimumStopVisits-PerLine (optional) - default is 1
- Maximum-TextLength (optional) - maximum length of strings in the reply. Default is 50. 

Example:

```xml
<siri:StopMonitoringRequest version="IL2.7" xsi:type="siri:StopMonitoringRequestStructure">
  <siri:RequestTimestamp>2012-10-31T09:39:39.480+02:00</siri:RequestTimestamp>
  <siri:MessageIdentifier xsi:type="siri:MessageQualifierStructure">0</siri:MessageIdentifier>
  <siri:PreviewInterval>PT1H</siri:PreviewInterval>
  <siri:MonitoringRef xsi:type="siri:MonitoringRefStructure">39795</siri:MonitoringRef>
  <siri:MaximumStopVisits>100</siri:MaximumStopVisits>
</siri:StopMonitoringRequest>
```



## The protocol: replies

The reply is composed of three parts

- Service Delivery - header, one per reply 
- Stop Monitoring Delivery - several per reply
- Payload - several per stop monitoring delivery. There are four types of payloads available: Monitored Stop Visit, Stop Line Notice, Monitored Stop Visit Cancelation & Stop Line Notice Cancelation. Only Monitored Stop Visit is relevant to our needs.

​    +--------------------------+      1       ∞       +---------------------------------------+      1       ∞      +-------------------------------+
​    |  Service Delivery  |   <------------>  |  Stop Monitoring Delivery  |   <------------>  | Monitored Stop Visit |
​    +--------------------------+                         +---------------------------------------+                       +--------------------------------+



### Service Delivery

That's the "header" of the all reply. Fields:

- Response Timestamp


- Producer Ref (Optional) - identifier of the data server
- Response Message Identifier (Optional) - identifier of the current response
- Request Message Ref (Optional) - identifier of the service request that triggered this response.
- Status (Optional) - False in case of an error, default True. If an error happened, there will be extra fields to describe the problem (CapabilityNotSupportedError, OtherError, Description)
- 0 or more Stop Monitoring Delivery 

example:

```xml
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
<S:Body>
  <ns5:GetStopMonitoringServiceResponse xmlns:ns2="http://www.ifopt.org.uk/acsb" xmlns:ns3="http://www.ifopt.org.uk/ifopt" xmlns:ns4="http://datex2.eu/schema/1_0/1_0" xmlns:ns5="http://new.webservice.namespace" xmlns:ns6="http://www.siri.org.uk/siri">
    <Answer>
      <ns6:ResponseTimestamp>2012-10-31T09:39:39.480+02:00</ns6:ResponseTimestamp>
      <ns6:ProducerRef>ISR Gateway</ns6:ProducerRef>
      <ns6:ResponseMessageIdentifier>118474</ns6:ResponseMessageIdentifier>
      <ns6:RequestMessageRef>0100700:1351669188:4684</ns6:RequestMessageRef>
      <ns6:Status>true</ns6:Status>
      ..... one or more StopMonitoringDelivery come here ...
        </Answer>
  </ns5:GetStopMonitoringServiceResponse>
</S:Body>
</S:Envelope>
```
### Stop Monitoring Delivery

Each Service Delivery contains one or more Stop Monitoring Delivery.

Fields:

* Version -  Current MoT production version is IL2.7 (11/2016). This is an attribute of the ```StopMonitoringDelivery``` element.
* Recorded At Time - Time stamp
* Request Message Ref (optional) - the identifier of the request that triggered this response.
* Status (optional)  - False if there's a problem in one of the replies (default true). If an error happened, there will be extra fields to describe the problem (CapabilityNotSupportedError, AccessNotAllowedError, NoInfoForTopicError, AllowedResourceUsageExceededError, OtherError)
* Valid Until (optional) - Range of time available for the server. Valid until is the maximum prediction time the server is capable of (it can be shorted than Data Horizon). If you requested prediction for a time after `valid until`, the response will be for `valid until`. So if you asked for data for 8pm, but the server only has prediction until 7pm, value until will be 7pm, and the results will be for 7pm.
* 0 or more payloads
* Note (optional)

Example:

```xml
<ns6:StopMonitoringDelivery version="IL2.6">
  <ns6:ResponseTimestamp>2012-10-31T09:39:39.496+02:00</ns6:ResponseTimestamp>
  <ns6:RequestMessageRef>0</ns6:RequestMessageRef>
  <ns6:Status>true</ns6:Status>
  <ns6:ValidUntil>2012-10-31T09:44:39.496+02:00</ns6:ValidUntil>
  ... on or more MonitoredStopVisit
</ns6:StopMonitoringDelivery>
```

### Payloads

There are four possible payloads, but only Monitored Stop Visit is relevant to our needs.

#### Monitored Stop Visit

- Recorded At Time
- Item Identifier (optional) 
- Monitoring Code - stop code?
- Monitored Vehicle Journey - data structure with the following fields. **all fields are optional**
  - Line Ref - route identifier, matches route id in the GTFS
  - Direction Ref - direction code, matches ??
  - Operator Reference - matches agency_id in the GTFS
  - JourneyPatternInfoGroup.PublishedLineName - the line number as displayed on the vehicles. Matches short_route_desc in the GTFS
  - Destination Ref - stop_code of the destination stop
  - Frame Vehicle Journey Ref . Dated Vehicle Journey Ref - trip_id from the GTFS
  - Vehicle Ref - a unique id of the vehicle, like the registration plate number 
  - Journey Progress Group . Confidence Level - reliability of the prediction. Default value probablyReliable. Other possible values: certain, veryReliable, reliable, probablyReliable, unconfirmed.
  - Progress Data - ?
  - Vehicle Location - current coordinate of the vehicle. Only available when the vehicle is on the move. Data structure with the two following sub-nodes:
    - Longitude
    - Latitude
  - Origin Aimed Departure Time - the planned departure time of the trip.
  - Monitored call, data structure with the following fields (**all fields are optional**):
    - Stop Point Ref - stop code for which this result was calculated, matches stop code in GTFS
    - Vehicle At Stop - boolean, whether the vehicle is in the stop. Default False.
    - Request Stop - does the vehicle call in the stop only if requested by a passenger, default false.
    - Destination Display - (not relevant)
    - Aimed Arrival Time - time where the vehicle is supposed to call at stop (relevant for trips that haven't started yet)
    - Actual Arrival Time - real time of arrival
    - Expected Arrival Time - prediction of time of arrival
    - Arrival Status -  possible values: onTime, early, delayed, cancelled, arrived, noReport. default noReport
    - Arrival Platform Name (not relevant)
    - Arrival Boarding Activity (not relevant)
    - Actual Departure Time - time vehicle left the stop
- Stop Visit Note (optional) - textual message



Example:

```xml
<ns3:MonitoredStopVisit>
  <ns3:RecordedAtTime>2016-12-18T11:40:13.000+02:00</ns3:RecordedAtTime>
  <ns3:ItemIdentifier>1053816062</ns3:ItemIdentifier>
  <ns3:MonitoringRef>21827</ns3:MonitoringRef>
  <ns3:MonitoredVehicleJourney>
      <ns3:LineRef>9813</ns3:LineRef>
      <ns3:DirectionRef>2</ns3:DirectionRef>
      <ns3:PublishedLineName>189</ns3:PublishedLineName>
      <ns3:OperatorRef>5</ns3:OperatorRef>
      <ns3:DestinationRef>26807</ns3:DestinationRef>
      <ns3:OriginAimedDepartureTime>2016-12-18T10:22:00.000+02:00</ns3:OriginAimedDepartureTime>
      <ns3:VehicleLocation>
        <ns3:Longitude>34.829524993896484</ns3:Longitude>                    
        <ns3:Latitude>32.10695266723633</ns3:Latitude>
      </ns3:VehicleLocation>
      <ns3:VehicleRef>634</ns3:VehicleRef>
      <ns3:MonitoredCall>
        <ns3:StopPointRef>21827</ns3:StopPointRef>
        <ns3:ExpectedArrivalTime>2016-12-18T11:41:00.000+02:00</ns3:ExpectedArrivalTime>
      </ns3:MonitoredCall>
  </ns3:MonitoredVehicleJourney>
</ns3:MonitoredStopVisit>
```









