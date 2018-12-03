FROM java:openjdk-8-jre

LABEL vendor="hasadna"
LABEL type="siri-collector"

ADD target/bus-0.0.1-SNAPSHOT.jar /opt/hasadna/bus.jar

CMD ["java", "-jar", "/opt/hasadna/bus.jar"]