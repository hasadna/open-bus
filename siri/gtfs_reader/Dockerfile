FROM java:openjdk-8-jre-alpine

LABEL vendor="hasadna"
LABEL type="gtfs-collector"

EXPOSE 8080
RUN mkdir -p /opt/hasadna/data/schedule_data
RUN mkdir -p /opt/hasadna/data/gtfs_schedules
RUN mkdir -p /opt/hasadna/data/siri_output

ADD target/siri-client-0.0.1-SNAPSHOT.jar /opt/hasadna/siri-client.jar

CMD ["java", "-Xmx2g", "-jar", "/opt/hasadna/siri-client.jar"]