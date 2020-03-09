# SIRI sub-project

This sub-project of open-bus is responsible for retrieving SIRI data for all buses, during all days of week.

This project consists of 2 Java projects, which run as 2 separate processes (JVMs): siri-retriever, and gtfs-reader.

The main branch used for this project is _siri-retriever-dev_.
All code changes in Java code should be done in branches that branch from _siri-retriever-dev_.

On the production machine (Ocean Digital 139.59.136.13), the running versions (of the 2 processes) are fetched from this branch!

## PRODUCTION machine operation
* access PROD machine through ssh
* cd to the correct sub-directory
(siri-retriever process: cd /home/evyatar/java/siri2/open-bus/siri/siri_retriever/siri-0.1/
 gtfs-reader process:    cd /home/evyatar/java/siri4-gtfsreader-update/open-bus/siri/gtfs_reader/
)

* switch to _siri-retriever-dev_ branch (if not already there).
* git status
* git pull
* git status
* kill currently running process
* execute the process again (using the sh file - either runSiri.sh or runGtfsReader.sh)
