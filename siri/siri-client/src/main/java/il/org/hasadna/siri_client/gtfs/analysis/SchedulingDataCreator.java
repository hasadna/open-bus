package il.org.hasadna.siri_client.gtfs.analysis;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import il.org.hasadna.siri_client.gtfs.crud.Route;
import il.org.hasadna.siri_client.gtfs.main.DefaultGtfsQueryBasedOnFtp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class SchedulingDataCreator {

    private static Logger logger = LoggerFactory.getLogger(SchedulingDataCreator.class);

    public SchedulingDataCreator() {
    }

    public void createScheduleForSiri(Collection<GtfsRecord> records, GtfsDataManipulations gtfs) {
        logger.info("size: {}", records.size());
        Function<GtfsRecord, String> f = new Function<GtfsRecord, String>() {
            @Override
            public String apply(GtfsRecord gtfsRecord) {
                return gtfsRecord.getTrip().getRouteId();
            }
        };
        logger.info("grouping trips of same route");
        Map<String, List<GtfsRecord>> tripsOfRoute = records.stream().collect(Collectors.groupingBy(f));
        logger.info("generating json for all routes...");

        // Filter!!! only  Dan(5), Superbus(16)
        List<String> onlyAgencies = Arrays.asList("5", "16");
        for (String agency : onlyAgencies) {
            List<SchedulingData> all =
                    tripsOfRoute.keySet().stream().
                            filter(routeId -> agency.equals(gtfs.getRoutes().get(routeId).getAgencyId())).
                            map(routeId -> {
                                String lineRef = routeId;
                                Route route = gtfs.getRoutes().get(routeId);
                                String makat = route.getRouteDesc().substring(0, 5);
                                String direction = route.getRouteDesc().split("-")[1];
                                String alternative = route.getRouteDesc().split("-")[2];
                                String stopCode = Integer.toString(tripsOfRoute.get(routeId).get(0).getLastStop().getStopCode());
                                String description = " --- Line " + route.getRouteShortName() +
                                        "  --- Makat " + makat +
                                        "  --- Direction " + direction +
                                        "  --- Alternative " + alternative +
                                        "  ------  " + calcDepartueTimesForRoute(routeId, tripsOfRoute);
                                String previewInterval = "PT2H";
                                String maxStopVisits = "7";
                                String executeEvery = "60";
                                SchedulingData sd = generateSchedulingData(description, stopCode, previewInterval, lineRef, maxStopVisits, executeEvery);
                                return sd;
                            }).
                            collect(Collectors.toList());
            logger.info("processed {} routes (agency {})", all.size(), agency);
            String json = "{  \"data\" :[" +
                    all.stream().
                            map(sd -> generateJson(sd)).
                            flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                            sorted().
                            collect(Collectors.joining(","))
                    + "]}";
            String fileName = "siri.schedule." + agency + ".json";
            logger.info("writing to file {}", fileName);
            writeToFile(fileName, json);
        }
        logger.info("schedules created.");
    }

    private void writeToFile(final String fileName, final String content) {
        try {
            Files.write(Paths.get(fileName), content.getBytes(Charset.forName("UTF-8")));
        } catch (IOException e) {
            logger.error("exception when writing json to file {}", fileName, e);
        }
    }

    private SchedulingData generateSchedulingData(String description, String stopCode, String previewInterval, String lineRef, String maxStopVisits, String executeEvery) {
        SchedulingData sd = new SchedulingData(description, stopCode, previewInterval, lineRef, maxStopVisits, executeEvery);
        return sd;
    }

    private Optional<String> generateJson(SchedulingData sd) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            mapper.enable(SerializationFeature.INDENT_OUTPUT);
            return Optional.of(mapper.writeValueAsString(sd));
        } catch (JsonProcessingException e) {
            logger.error("absorbing exception while creating scheduling data for route {}", sd.lineRef, e);
            return Optional.empty();
        }
    }

    private String calcDepartueTimesForRoute(String routeId, Map<String, List<GtfsRecord>> tripsOfRoute) {
        List<GtfsRecord> allTrips = tripsOfRoute.get(routeId);
        String departureTimes =
                allTrips.stream().
                        map(gtfsRecord -> gtfsRecord.getFirstStopTime().getDepartureTime()).
                        map(stopTime -> stopTime.substring(0, 5)).
                        sorted().
                        collect(Collectors.joining(","));
        return departureTimes;
    }


    //                {
//                    "description" : "947 Haifa-Jer",
//                        "stopCode" : "6109",
//                        "previewInterval" : "PT2H",
//                        "lineRef" : "19740",
//                        "maxStopVisits" : 7,
//                        "executeEvery" : 60
//                }
    private class SchedulingData {
        public String description;
        public String stopCode;
        public String previewInterval;
        public String lineRef;
        public String maxStopVisits;
        public String executeEvery;

        public SchedulingData(String description, String stopCode, String previewInterval, String lineRef, String maxStopVisits, String executeEvery) {
            this.description = description;
            this.stopCode = stopCode;
            this.previewInterval = previewInterval;
            this.lineRef = lineRef;
            this.maxStopVisits = maxStopVisits;
            this.executeEvery = executeEvery;
        }
    }

}
