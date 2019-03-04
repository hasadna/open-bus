FROM java:openjdk-8-jre-alpine

LABEL vendor="hasadna"
LABEL type="siri-collector"

EXPOSE 8080
RUN mkdir -p /opt/hasadna/data/schedule_data
RUN mkdir -p /opt/hasadna/data/gtfs_schedules
RUN mkdir -p /opt/hasadna/data/siri_output

ADD target/bus-0.0.1-SNAPSHOT.jar /opt/hasadna/bus.jar

CMD ["java", "-jar", "/opt/hasadna/bus.jar"]