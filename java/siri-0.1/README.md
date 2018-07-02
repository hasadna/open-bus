# SIRI client Spring Boot application

## In Short
This application is a Spring Boot application, written in Java.

Its main purpose is to query the MOT (Ministry of Transportation) server for SIRI data.

After cloning this branch of Git, open a console window and do:
```bash
  cd siri-0.1 
  ./mvnw clean package -DskipTests  
  java -jar ./target/bus-0.0.1-SNAPSHOT.jar 
```
(on Windows replace every / with \)

## Background
As part of the open-bus project in הסדנה לידע ציבורי , this application retrieves (from MOT Siri Server) all real-time data about the public transportation buses in Israel, their locations and arrival times.

This SIRI retrieved data can then be combined with GTFS data to get useful insights. This part is not covered by this application!

This application, in the micro-services architectural style, limits itself to retrieving and storing the SIRI real-time data (so it can later be used in various ways).

## Context View
The application constantly retrieves data from MOT SIRI server by sending SOAP request, and receiving SOAP responses.

The applications parses the SOAP responses, and creates CSV lines containing the useful data from each response.

The application stores all useful data that was retrieved in CSV (text) files. (These files can later be imported to a relational database, or processed in any other way).

The application uses an internal JSON file with details on which bus routes to query, and how frequently.

(embed drawing here)



## Functional View

## Information View

## Development View

# FAQ