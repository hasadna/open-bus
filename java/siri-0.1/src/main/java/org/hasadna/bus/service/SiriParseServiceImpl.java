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
                logger.info("answer.isStatus={}", sm.getAnswer().isStatus());
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

                Date recordedAt = visit.getRecordedAtTime();
                Date departureTime = visit.getMonitoredVehicleJourney().getOriginAimedDepartureTime();
                String operatorRef = visit.getMonitoredVehicleJourney().getOperatorRef().getValue();
                String journeyRef = visit.getMonitoredVehicleJourney().getFramedVehicleJourneyRef().getDatedVehicleJourneyRef();
                String rep = stringRepresentation(lineRef, lineName, recordedAt, expectedArrivalTime, licensePlate, lat, lon, departureTime, operatorRef, journeyRef, responseTimestamp);
                String jsonStrRepresentation = buildJson(lineRef, lineName, recordedAt, expectedArrivalTime, licensePlate, lat, lon, departureTime, operatorRef, journeyRef);
                s = s + rep + "\n";
            }
            if (!visits.isEmpty()) {
                logger.info("produced summary: {}", s);
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

    private String buildJson(String lineRef, String lineName, Date recordedAt, Date expectedArrivalTime, String licensePlate, BigDecimal lat, BigDecimal lon, Date departureTime, String operatorRef, String journeyRef) {
        return "" ; // temporary
    }


    private String stringRepresentation(String lineRef, String lineName, Date recordedAt, Date expectedArrivalTime, String licensePlate, BigDecimal lon, BigDecimal lat, Date departureTime, String operatorRef, String journeyRef, String responseTimestamp) {
        String s = MessageFormat.format("{10},[line {0} v {1} oad {6} ea {2}],{7},{8},{0},{9},{6},{1},{2},{3},{4},{5}",
                lineName, licensePlate,
                formatTimeHHMM(expectedArrivalTime),
                formatTime(recordedAt),
                lon.toString(), lat.toString(),
                formatTimeHHMM(departureTime),
                operatorRef, lineRef, journeyRef, responseTimestamp
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
