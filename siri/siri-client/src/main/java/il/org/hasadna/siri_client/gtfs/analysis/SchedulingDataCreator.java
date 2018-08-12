package il.org.hasadna.siri_client.gtfs.analysis;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import il.org.hasadna.siri_client.gtfs.crud.Route;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.format.TextStyle;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class SchedulingDataCreator {

    private static Logger logger = LoggerFactory.getLogger(SchedulingDataCreator.class);

    public SchedulingDataCreator() {
    }

    Function<GtfsRecord, String> f = new Function<GtfsRecord, String>() {
        @Override
        public String apply(GtfsRecord gtfsRecord) {
            return gtfsRecord.getTrip().getRouteId();
        }
    };

    private boolean predicatSameAgency(final String routeId, final String agency, final GtfsDataManipulations gtfs) {
        try {
            logger.trace("gtfs={}", gtfs);
            logger.trace("gtfs.getRoutes() has {} items", gtfs.getRoutes().size());
            logger.trace("gtfs.getRoutes().get(routeId)={}", gtfs.getRoutes().get(routeId));
            logger.trace("gtfs.getRoutes().get(routeId).getAgencyId()={}", gtfs.getRoutes().get(routeId).getAgencyId());
            return agency.equals(gtfs.getRoutes().get(routeId).getAgencyId());
        }
        catch (Exception ex) {
            logger.warn("absorbing exception for agency {}, routeId {}", agency, routeId, ex);
            return false;
        }
    }

    public void createScheduleForSiri(final Collection<GtfsRecord> records, final GtfsDataManipulations gtfs, final String toDir, final List<String> onlyAgencies, final LocalDate date) {
        logger.trace("creating schedule, size: {}", records.size());

        logger.info("grouping trips of same route");
        Map<String, List<GtfsRecord>> tripsOfRoute = records.stream().collect(Collectors.groupingBy(f));
        logger.info("generating json for all routes...");

        // Filter!!! only  Dan(5), Superbus(16)
        //List<String> onlyAgencies = Arrays.asList("5", "16");
        for (String agency : onlyAgencies) {
            List<SchedulingData> all =
                    tripsOfRoute.keySet().stream().
                            filter(routeId -> predicatSameAgency(routeId, agency, gtfs)).
                            map(routeId -> calcSchedulingData(routeId, gtfs, date, tripsOfRoute)).
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
            DateTimeFormatter x = DateTimeFormatter.ISO_DATE ;
            String archiveFileName = "siri.schedule." + agency + "." + dayNameFromDate(date) + ".json." + x.format(date) ;
            logger.info("writing to file {} (in {})", fileName, toDir);
            writeToFile(toDir, fileName, json);
            writeToFile(toDir, archiveFileName, json);
        }
        logger.info("schedules created.");
    }

    private SchedulingData calcSchedulingData(final String routeId, final GtfsDataManipulations gtfs, LocalDate date, Map<String, List<GtfsRecord>> tripsOfRoute) {
        String lineRef = routeId;
        Route route = gtfs.getRoutes().get(routeId);
        String desc1 = parseLongName(route.getRouteLongName());
        String makat = route.getRouteDesc().substring(0, 5);
        String direction = route.getRouteDesc().split("-")[1];
        String alternative = route.getRouteDesc().split("-")[2];
        String stopCode = Integer.toString(tripsOfRoute.get(routeId).get(0).getLastStop().getStopCode());
        String desc2 = "קו " + route.getRouteShortName() + " " + desc1 ;
        Map<DayOfWeek, List<String>> departureTimes = calcDepartueTimesAllWeek(routeId, gtfs, date);
        TreeMap<DayOfWeek, List<String>> depSorted = new TreeMap<>(
                (Comparator<DayOfWeek>) (o1, o2) ->  {
                    if (o1.equals(DayOfWeek.SUNDAY)) return -1 ;
                    else if (o2.equals(DayOfWeek.SUNDAY)) return 1 ;
                    else return o1.getValue() - o2.getValue();
                }
        );
        if (departureTimes == null) {
            logger.warn("departureTimes is null. routeId={}, date={}", routeId, date);
        }
        else {
            depSorted.putAll(departureTimes);
        }
        String description = " --- " + desc2 +
                "  --- Makat " + makat +
                "  --- Direction " + direction +
                "  --- Alternative " + alternative +
                "  ------  " + dayNameFromDate(date) +
                "  ------  " + depSorted.get(date.getDayOfWeek()) ;
        String previewInterval = "PT2H";
        String maxStopVisits = "7";
        String executeEvery = "60";
        Map<DayOfWeek, String> lastArrivals = new HashMap<>();
        lastArrivals.put(date.getDayOfWeek(), calcLastServiceArrivalTime(routeId, tripsOfRoute));
        SchedulingData sd = generateSchedulingData(description, makat, route.getRouteShortName(), stopCode, previewInterval, lineRef, maxStopVisits, executeEvery, depSorted, lastArrivals);
        return sd;
    }


    public MakatFile makatFile = null;

    private Map<DayOfWeek,List<String>> calcDepartueTimesAllWeek(String routeId, GtfsDataManipulations gtfs, LocalDate originalDate) {
        logger.trace("calcDepartueTimesAllWeek {} {}", routeId, originalDate);
        if (makatFile == null) {
            makatFile = new MakatFile();
            makatFile.init();
        }
        Map<DayOfWeek, List<String>> departureTimes = new HashMap<>();
        try {
            departureTimes = makatFile.findDeparturesByRouteId(routeId, originalDate);
        }
        catch (Exception e) {
            logger.error("absorbing", e);
        }
        return departureTimes;
    }

    public static String dayNameFromDate(LocalDate date) {
        return date.getDayOfWeek().getDisplayName(TextStyle.FULL, Locale.CANADA);
    }

    private String parseLongName(String routeLongName) {
        String result = "";
        try {
            String[] parts = routeLongName.split("<->");
            if (parts.length == 2) {
                String from = parts[0];
                String fromCity = from.split("-")[1];

                String to = parts[1];
                String toCity = to.split("-")[1];

                if (fromCity.equals(toCity)) {
                    result = "ב" +fromCity ;
                }
                else {
                    result = "מ" +fromCity + " אל" + " " + toCity;
                }
            }
        }
        catch (Exception ex) {
            // parsing failed, so
            result = "";
        }
        return result;
    }

    private void writeToFile(String toDir, final String fileName, final String content) {
        try {
            if (!toDir.endsWith("/")) {
                toDir = toDir + "/";
            }
            Files.write(Paths.get(toDir + fileName), content.getBytes(Charset.forName("UTF-8")));
        } catch (IOException e) {
            logger.error("exception when writing json to file {}", fileName, e);
        }
    }

    private SchedulingData generateSchedulingData(String description, String makat, String lineShortName, String stopCode, String previewInterval, String lineRef, String maxStopVisits, String executeEvery, Map<DayOfWeek, List<String>> departureTimes, Map<DayOfWeek, String> lastArrivalTimes) {
        SchedulingData sd = new SchedulingData(description, makat, lineShortName, stopCode, previewInterval, lineRef, maxStopVisits, executeEvery, departureTimes, lastArrivalTimes);
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

    private String calcLastServiceArrivalTime(String routeId, Map<String, List<GtfsRecord>> tripsOfRoute) {
        List<GtfsRecord> allTrips = tripsOfRoute.get(routeId);
        String lastArrival = allTrips.stream()
                .map(gtfsRecord -> gtfsRecord.getLastStopTime().getArrivalTime())
                .collect(Collectors.maxBy(Comparator.naturalOrder())).orElse("23:59");
        return lastArrival;
    }

    private List<String> calcDepartueTimesForRoute(String routeId, Map<String, List<GtfsRecord>> tripsOfRoute) {
        List<GtfsRecord> allTrips = tripsOfRoute.getOrDefault(routeId, new ArrayList<>());
        List<String> departureTimes =
                allTrips.stream().
                        map(gtfsRecord -> gtfsRecord.getFirstStopTime().getDepartureTime()).
                        map(stopTime -> stopTime.substring(0, 5)).
                        sorted().
                        collect(Collectors.toList());
        return departureTimes;
    }


    private class SchedulingData {
        public String description;
        public String makat;
        public String lineShortName;
        public String stopCode;
        public String previewInterval;
        public String lineRef;
        public String maxStopVisits;
        public String executeEvery;
        public List<LocalTime[]> activeRanges;
        public Map<DayOfWeek, List<String>> weeklyDepartureTimes;
        public Map<DayOfWeek, String> lastArrivalTimes;

        public SchedulingData(String description, String makat, String lineShortName, String stopCode, String previewInterval, String lineRef, String maxStopVisits, String executeEvery, Map<DayOfWeek, List<String>> departureTimes, Map<DayOfWeek, String> lastArrivalTimes) {
            this.description = description;
            this.makat = makat;
            this.lineShortName = lineShortName;
            this.stopCode = stopCode;
            this.previewInterval = previewInterval;
            this.lineRef = lineRef;
            this.maxStopVisits = maxStopVisits;
            this.executeEvery = executeEvery;
            this.weeklyDepartureTimes = departureTimes;
            this.lastArrivalTimes = lastArrivalTimes;
        }
    }

}
