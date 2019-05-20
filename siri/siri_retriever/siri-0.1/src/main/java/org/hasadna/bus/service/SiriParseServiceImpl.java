package org.hasadna.bus.service;

import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import uk.org.siri.siri.MonitoredStopVisitStructure;
import uk.org.siri.siri.StopMonitoringDeliveriesStructure;
import uk.org.siri.siri.StopMonitoringDeliveryStructure;

import java.math.BigDecimal;
import java.text.MessageFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Component
public class SiriParseServiceImpl implements SiriParseService {

    protected final Logger logger = LoggerFactory.getLogger(SiriParseServiceImpl.class);

    @Override
    public Optional<String> parseShortSummary(GetStopMonitoringServiceResponse sm) {
        try {
            if ((sm == null) || (sm.getAnswer() == null)) {
                return Optional.empty();
            }
            if (sm.getAnswer().isStatus() != null) {
                logger.trace("answer.isStatus={}", sm.getAnswer().isStatus());
            }
            SortedMap<String, MonitoredStopVisitStructure> visits = new TreeMap<>();
            Set<String> licensePlates = new HashSet<>();
            for (StopMonitoringDeliveryStructure smd : sm.getAnswer().getStopMonitoringDelivery()) {
                for (MonitoredStopVisitStructure visit : smd.getMonitoredStopVisit()) {
                    if (visit.getMonitoredVehicleJourney().getVehicleRef() == null) {
                        //logger.warn("null vehicleRef");
                        continue;
                    }
                    String licensePlate = visit.getMonitoredVehicleJourney().getVehicleRef().getValue();
                    if (licensePlates.contains(licensePlate)) {
                        continue;   // TODO check if rest of the data is also the same
                    }
                    Date departureTime = visit.getMonitoredVehicleJourney().getOriginAimedDepartureTime();
                    licensePlates.add(licensePlate);
                    visits.put(formatDate(departureTime) + "/" + licensePlate, visit);
                }
            }
            String s = "";
            String responseTimestamp = formatDate(sm.getAnswer().getResponseTimestamp());
            s = "";//s + "\n" + date + "\n";
            for (String key : visits.keySet()) {
                MonitoredStopVisitStructure visit = visits.get(key);
                String licensePlate = visit.getMonitoredVehicleJourney().getVehicleRef().getValue();
                String lineRef = visit.getMonitoredVehicleJourney().getLineRef().getValue();
                visit.getMonitoredVehicleJourney().getMonitoredCall().isVehicleAtStop();
                Date expectedArrivalTime = visit.getMonitoredVehicleJourney().getMonitoredCall().getExpectedArrivalTime();
                BigDecimal lon = BigDecimal.ZERO;
                BigDecimal lat = BigDecimal.ZERO;
                if (visit.getMonitoredVehicleJourney().getVehicleLocation() != null) {
                    lon = visit.getMonitoredVehicleJourney().getVehicleLocation().getLongitude();
                    lat = visit.getMonitoredVehicleJourney().getVehicleLocation().getLatitude();
                }
                String lineName = visit.getMonitoredVehicleJourney().getPublishedLineName().getValue();
                visit.getMonitoredVehicleJourney().getDestinationRef();
                String direction = visit.getMonitoredVehicleJourney().getDirectionRef().getValue();

                Date recordedAt = visit.getRecordedAtTime();
                Date departureTime = visit.getMonitoredVehicleJourney().getOriginAimedDepartureTime();
                String operatorRef = visit.getMonitoredVehicleJourney().getOperatorRef().getValue();
                String journeyRef = visit.getMonitoredVehicleJourney().getFramedVehicleJourneyRef().getDatedVehicleJourneyRef();
                String dataFrameRef = visit.getMonitoredVehicleJourney().getFramedVehicleJourneyRef().getDataFrameRef().getValue();
                String rep = stringRepresentation(lineRef, lineName, recordedAt, expectedArrivalTime, licensePlate, lat, lon, departureTime, operatorRef, journeyRef, responseTimestamp, dataFrameRef);
                s = s + rep + "\n";
            }
            if (!visits.isEmpty()) {
                logger.trace("produced summary: {}", s);
                return Optional.of(s);
            }
            else {
                return Optional.empty();
            }
        }
        catch (Exception ex) {
            logger.error("unhandled exception in parsing", ex);
            return Optional.empty();
        }
    }


    private String stringRepresentation(String lineRef, String lineName, Date recordedAt, Date expectedArrivalTime, String licensePlate, BigDecimal lon, BigDecimal lat, Date departureTime, String operatorRef, String journeyRef, String responseTimestamp, String dataFrameRef) {
        String s = MessageFormat.format("{10},[line {0} v {1} oad {12} ea {11}],{7},{8},{0},{9},{6},{1},{2},{3},{4},{5},{13}",
                lineName, licensePlate,
                formatDate(expectedArrivalTime),    // expectedArrivalTime should include both date and time - // <ns3:ExpectedArrivalTime>2019-04-01T21:14:00.000+03:00</ns3:ExpectedArrivalTime>
                formatDate(recordedAt),             // recordedAt should include both date and time
                lon.toString(), lat.toString(),
                formatDate(departureTime),          // OriginAimedDeparture should include both date and time - // <ns3:OriginAimedDepartureTime>2019-04-01T20:00:00.000+03:00</ns3:OriginAimedDepartureTime>
                operatorRef, lineRef, journeyRef, responseTimestamp,
                formatTimeHHMM(expectedArrivalTime),    // ea as time only, for the free text part
                dataFrameRef
        );
        return s ;
    }

    private String formatDate(Date date) {
        LocalDateTime ldt = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        String asStr = DateTimeFormatter.ISO_DATE_TIME.format(ldt);
        return asStr;
    }

    private String formatTime(Date date) {
        String dateTime = formatDate(date);
        return dateTime.split("T")[1];
    }

    private String formatTimeHHMM(Date date) {
        String dateTime = formatDate(date);
        return dateTime.split("T")[1].substring(0,5);
    }

}

/*
<ns3:MonitoredVehicleJourney><ns3:LineRef>5962</ns3:LineRef><ns3:DirectionRef>1</ns3:DirectionRef><ns3:FramedVehicleJourneyRef><ns3:DataFrameRef>2019-04-01</ns3:DataFrameRef><ns3:DatedVehicleJourneyRef>31439164</ns3:DatedVehicleJourneyRef></ns3:FramedVehicleJourneyRef><ns3:PublishedLineName>174</ns3:PublishedLineName><ns3:OperatorRef>4</ns3:OperatorRef><ns3:DestinationRef>60664</ns3:DestinationRef><ns3:OriginAimedDepartureTime>2019-04-01T20:36:00.000+03:00</ns3:OriginAimedDepartureTime><ns3:VehicleLocation><ns3:Longitude>35.29014587402344</ns3:Longitude><ns3:Latitude>31.76877212524414</ns3:Latitude></ns3:VehicleLocation><ns3:VehicleRef>7558569</ns3:VehicleRef><ns3:MonitoredCall><ns3:StopPointRef>60664</ns3:StopPointRef><ns3:ExpectedArrivalTime>2019-04-01T21:18:00.000+03:00</ns3:ExpectedArrivalTime></ns3:MonitoredCall></ns3:MonitoredVehicleJourney>

<ns3:MonitoredVehicleJourney>
    <ns3:LineRef>5962</ns3:LineRef>
    <ns3:DirectionRef>1</ns3:DirectionRef>
    <ns3:FramedVehicleJourneyRef>
        <ns3:DataFrameRef>2019-04-01</ns3:DataFrameRef>
        <ns3:DatedVehicleJourneyRef>31439164</ns3:DatedVehicleJourneyRef>
    </ns3:FramedVehicleJourneyRef>
    <ns3:PublishedLineName>174</ns3:PublishedLineName>
    <ns3:OperatorRef>4</ns3:OperatorRef>
    <ns3:DestinationRef>60664</ns3:DestinationRef>
    <ns3:OriginAimedDepartureTime>2019-04-01T20:36:00.000+03:00</ns3:OriginAimedDepartureTime>
    <ns3:VehicleLocation>
        <ns3:Longitude>35.29014587402344</ns3:Longitude>
        <ns3:Latitude>31.76877212524414</ns3:Latitude>
    </ns3:VehicleLocation>
    <ns3:VehicleRef>7558569</ns3:VehicleRef>
    <ns3:MonitoredCall>
        <ns3:StopPointRef>60664</ns3:StopPointRef>
        <ns3:ExpectedArrivalTime>2019-04-01T21:18:00.000+03:00</ns3:ExpectedArrivalTime>
    </ns3:MonitoredCall>
</ns3:MonitoredVehicleJourney>

*/