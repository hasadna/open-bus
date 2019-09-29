**Siri Client - Java**

This application is a Spring Boot application, written in Java.

Its main purpose is to query the MOT (Ministry of Transportation) server for SIRI data.

To develop, or just run locally, clone this branch (java-siri-client) of the Git repository to your local machine, and then do:
```bash
  cd siri-0.1  # move to root directory of project 

  ./mvnw clean  # use the built-in maven (on Windows use mvnw.cmd instead)

  ./mvnw clean package -DskipTests  # create the executable jar in ./target directory

  java -jar ./target/bus-0.0.1-SNAPSHOT.jar     # run the application
```

The application runs properly on the cloud machine (139.59.136.13), but on your local machine it will fail to receive data from MOT server (because MOT server allows only requests from IP 139.59.136.13).

However, on your local machine we simulate SIRI responses, so you can develop on your local machine.

For more details, or if you have some problems compiling and running, see siri-0.1/README.md 

