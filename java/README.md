**Siri Client - Java**

This application is a Spring Boot application, written in Java.

Its main purpose is to query the MOT (Ministry of Transportation) server for SIRI data.

To see if all is OK, do:

  cd siri-0.1

  ./mvnw clean

  ./mvnw clean package -DskipTests


It runs properly on the cloud machine (139.59.136.13), but on your local machine it will fail to receive data from MOT server (because it allows only requests from IP 139.59.136.13).

However, on your local machine we simulate SIRI responses, so you can develop on your local machine.

For more details, see siri-0.1/README.md 

