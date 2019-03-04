package il.org.hasadna.siri_client.gtfs.analysis;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import il.org.hasadna.siri_client.gtfs.crud.Route;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.format.TextStyle;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

//    private List<String> listOfRouteIdsWeWantToTrack = Arrays.asList(
//            // KG to Beer7 (15+31)
//            10869,10868,8140,8141,8145,8148,8151,8162,8165,8153,8164,8155,16407,13582,13581,11492,11493,11494,16587,16586,16582,16583,
//            // HaMovil 7+8
//            10170, 10169,            8311,            8312,            8274,            8275,            10862,            10861,            1606,
//            1605,            1604,            1607,            17408,            17407,            1421,            1419,            10859,
//            10860,            17813,            17812,            18881,            18882,            1620,            1621,            1617,
//            1619,            1618).stream().map(num -> Integer.toString(num)).collect(Collectors.toList());

//    private List<String> listOfMakatsWeWantToTrack =
//            Arrays.asList("12348","11367","10368","10369","12469","13371","13250","12240",  // KGAT to Beer7
//                    "10337","17032","11334","11303","10342","16353","16058","22047","13280","21352","11554","11553" // Zomet HaMovil
//            );

    // routes from Dan's Polygon processing
    private List<String> listOfRouteIdsWeWantToTrack = Arrays.asList(15822, 21327, 4137, 11658, 16379, 2739, 21901, 19638, 11943, 11657, 4143, 6544, 1606, 14136, 6547, 11539, 11842, 9261, 13616, 4475, 3890, 6558, 20562, 7693, 5242, 1569, 8247, 11297, 18881, 12366, 1123, 22289, 9813, 9258, 14795, 19640, 5266, 7251, 4401, 10982, 7221, 1172, 9259, 2597, 17724, 3908, 6533, 3883, 14988, 13756, 6540, 8236, 17131, 13428, 3315, 9786, 3578, 13429, 15003, 3894, 8133, 10330, 15763, 6567, 14134, 11946, 2494, 5308, 7526, 22306, 20915, 4448, 8244, 1171, 2280, 17193, 3636, 10259, 19796, 1042, 4151, 3311, 17720, 10021, 19703, 2486, 16077, 1078, 11782, 1080, 9802, 13386, 14168, 9233, 11359, 18254, 14798, 4423, 11098, 20958, 8241, 132, 11681, 9924, 9760, 11077, 11117, 9147, 9758, 13615, 19668, 22309, 13783, 20922, 14179, 14571, 10375, 10926, 9852, 2482, 23069, 11692, 1150, 21934, 1576, 17220, 10880, 23188, 15373, 19378, 17918, 11293, 15764, 8457, 9253, 10879, 19639, 17919, 4142, 1017, 4149, 4135, 20851, 14791, 11777, 3794, 9494, 20666, 17491, 14792, 12364, 15002, 21900, 4474, 19379, 10921, 3577, 10223, 2278, 21735, 6546, 9825, 10374, 18504, 16801, 1153, 19919, 6563, 5269, 11694, 12354, 19654, 22302, 6541, 1175, 8237, 14171, 12365, 83, 19635, 1121, 21933, 4418, 3325, 1107, 6534, 16384, 22294, 8248, 11683, 13753, 8454, 19665, 11289, 1079, 7565, 1178, 22400, 7305, 2953, 17026, 22211, 9146, 9493, 2488, 5240, 14187, 1074, 1077, 17723, 17194, 11783, 9265, 9803, 7695, 3877, 22287, 19795, 2567, 9742, 19735, 11116, 2776, 14564, 17496, 14176, 22115, 7525, 17721, 1170, 4157, 4447, 3891, 9234, 9497, 4146, 11358, 10258, 4154, 14989, 11097, 6535, 9923, 10925, 14133, 9454, 4453, 17417, 12353, 22399, 1577, 17109, 19672, 3318, 16382, 20667, 20813, 19667, 1110, 14797, 4396, 11322, 9251, 19008, 9254, 15823, 22307, 20914, 4403, 9851, 9142, 8245, 20113, 9811, 23187, 10924, 4440, 2484, 8238, 4134, 17050, 16385, 11013, 19670, 20112, 4450, 2454, 13384, 23186, 14166, 16407, 1570, 4488, 19776, 23117, 8249, 11295, 9144, 16800, 20849, 5237, 3372, 10262, 20924, 11688, 1146, 21676, 14170, 4444, 16791, 7201, 5236, 18006, 19636, 17035, 9915, 10020, 9627, 21736, 17920, 12011, 8455, 10908, 17960, 2492, 9495, 3791, 19634, 19666, 20953, 2596, 14184, 9281, 14138, 6542, 2952, 11695, 1604, 14177, 11684, 1174, 4637, 22785, 14800, 9224, 2533, 17043, 9756, 3633, 22308, 3884, 14565, 4446, 3317, 2566, 17130, 9154, 17024, 17722, 16216, 9257, 18007, 22780, 10977, 9455, 11784, 9285, 21073, 9788, 17827, 20812, 21677, 17027, 2457, 14796, 15940, 11197, 21326, 6553, 20850, 11944, 9240, 2439, 17414, 10955, 10790, 1095, 17497, 19740, 2713, 19775, 3322, 9453, 22286, 11685, 15738, 23070, 16214, 4405, 14808, 1019, 9785, 9255, 4439, 18795, 2264, 10263, 11696, 22220, 17025, 9141, 12356, 23116, 6543, 2600, 10923, 8239, 6575, 9496, 19633, 2724, 4451, 18426, 14185, 1575, 1605, 9850, 1098, 6548, 6532, 2266, 19734, 13281, 11689, 9827, 2441, 17961, 9260, 6572, 21086, 8243, 6561, 20561, 4402, 3893, 15041, 1173, 1630, 2598, 9277, 12012, 4636, 1116, 21054, 9266, 11306, 9498, 2738, 19637, 4455, 9849, 16790, 13618, 17826, 9744, 7220, 14167, 2495, 11682, 9252, 14169, 1021, 2485, 1607, 1097, 9225, 9267, 1043, 21053, 4152, 3310, 1177, 15040, 18882, 8242, 9456, 17418, 22303, 17036, 17415, 19674, 16380, 9356, 11196, 14178, 4483, 10791, 8246, 3323, 131, 4394, 10976, 7563, 11693, 4155, 9789, 19380, 2490, 9452, 9755, 2532, 12675, 2489, 11051, 9256, 22781, 7198,
            1075).stream().map(num -> Integer.toString(num)).collect(Collectors.toList());;

    public void createScheduleForSiri(final Collection<GtfsRecord> records, final GtfsDataManipulations gtfs, final String toDir, final List<String> onlyAgencies, final LocalDate date) {
        logger.trace("creating schedule, size: {}", records.size());

        logger.info("grouping trips of same route");
        Map<String, List<GtfsRecord>> tripsOfRoute = records.stream().collect(Collectors.groupingBy(f));
        logger.info("generating json for all routes...");

        // Filter!!! only  Dan(5), Superbus(16)
        //List<String> onlyAgencies1 = new ArrayList<>();      // temporary - try not according to Agencies
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


        // adding misc lines (not according to agencies)
        // addSchedulesByMakat - this implementation might be too slow
//        List<SchedulingData> addByMakat =
//                tripsOfRoute.keySet().stream().
//                        filter(routeId -> makatIsInList(routeId, gtfs, records, date)).
//                        map(routeId -> calcSchedulingData(routeId, gtfs, date, tripsOfRoute)).
//                        collect(Collectors.toList());
        // addSchedulesByRoute
//        List<SchedulingData> addByRouteIds =
//                tripsOfRoute.keySet().stream().
//                        filter(routeId -> routeIdIsInList(routeId, gtfs)).
//                        map(routeId -> calcSchedulingData(routeId, gtfs, date, tripsOfRoute)).
//                        collect(Collectors.toList());
//        List<SchedulingData> all = new ArrayList<>();
//        //all.addAll(addByMakat);
//        all.addAll(addByRouteIds);
//        addTheseSchedules(all, "misc2", date, toDir);    // will write to dir toDir a file named "siri.schedule.misc.json" containing scheduling for all makats and routes
//        logger.info("schedules created.");
    }

    private boolean routeIdIsInList(String routeId, GtfsDataManipulations gtfs) {
        return listOfRouteIdsWeWantToTrack.contains(routeId);
    }

//    private boolean makatIsInList(String routeId, GtfsDataManipulations gtfs,
//                                  final Collection<GtfsRecord> records, LocalDate date) {
//        // find makat of routeId
//        Set<String> makat = findMakats(Arrays.asList(routeId),records,gtfs,date);
//        return listOfMakatsWeWantToTrack.contains(makat);
//    }

    private void addTheseSchedules(final List<SchedulingData> all,
                                   final String fileNameInfix,
                                   final LocalDate date,
                                   final String toDir) {
        logger.info("processed {} routes (added by makat or routeId)", all.size());
        String json = "{  \"data\" :[" +
                all.stream().
                        map(sd -> generateJson(sd)).
                        flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                        sorted().
                        collect(Collectors.joining(","))
                + "]}";
        String fileName = "siri.schedule." + fileNameInfix + ".json";
        DateTimeFormatter x = DateTimeFormatter.ISO_DATE ;
        String archiveFileName = "siri.schedule." + fileNameInfix + "." + dayNameFromDate(date) + ".json." + x.format(date) ;
        logger.info("writing to file {} (in {})", fileName, toDir);
        writeToFile(toDir, fileName, json);
        writeToFile(toDir, archiveFileName, json);
    }

    public Set<String> findMakats(final List<String> routeIds,
                                   final Collection<GtfsRecord> records,
                                   final GtfsDataManipulations gtfs,
                                   final LocalDate date) {
        Set<String> makats = new HashSet<>();
        Map<String, List<GtfsRecord>> tripsOfRoute = records.stream().collect(Collectors.groupingBy(f));
        for (String routeId : routeIds) {
            SchedulingData sd = calcSchedulingData(routeId, gtfs, date, tripsOfRoute);
            if (sd != null && sd.makat != null) {
                makats.add(sd.makat);
            }
        }
        return makats;
    }

    public Optional<String> generateJsonFor(final String routeId,
                                final Collection<GtfsRecord> records,
                                final GtfsDataManipulations gtfs,
                                final LocalDate date) {
        Map<String, List<GtfsRecord>> tripsOfRoute = records.stream().collect(Collectors.groupingBy(f));
        Optional<String> innerJson = generateJson(calcSchedulingData(routeId, gtfs, date, tripsOfRoute));
        if (innerJson.isPresent()) {
            logger.info("json={}", innerJson.get());
        }
        //String json = "{  \"data\" :[" + innerJson + "]}";
        return innerJson;
    }

    private SchedulingData calcSchedulingData(final String routeId, final GtfsDataManipulations gtfs, LocalDate date, Map<String, List<GtfsRecord>> tripsOfRoute) {
        String lineRef = routeId;
        Route route = gtfs.getRoutes().get(routeId);
        if (route == null) {
            logger.error("route with Id {} was not found in GTFS file", routeId);
            return null;
        }
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
            makatFile.init(originalDate);
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
            if (sd == null) {
                return Optional.empty();
            }
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
