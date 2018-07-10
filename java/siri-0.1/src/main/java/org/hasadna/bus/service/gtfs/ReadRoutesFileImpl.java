package org.hasadna.bus.service.gtfs;

import org.hasadna.bus.entity.gtfs.Calendar;
import org.hasadna.bus.entity.gtfs.Route;
import org.hasadna.bus.entity.gtfs.Stop;
import org.hasadna.bus.entity.gtfs.StopTimes;
import org.hasadna.bus.entity.gtfs.Trip;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import javax.annotation.PostConstruct;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Component
@Profile("gtfs")
public class ReadRoutesFileImpl implements ReadRoutesFile {

    @Value("${gtfs.dir.location:/home/evyatar/work/hasadna/open-bus/gtfs/GTFS-2018-06-20/}")
    private String dirOfGtfsFiles ;
            //"/home/evyatar/Downloads/israel-public-transportation May 2018/" ;
    private String fileName = "routes.txt";
    private String fullPath = dirOfGtfsFiles + fileName;

    private String tripsFileName = "trips.txt";
    private String tripsFullPath = dirOfGtfsFiles + tripsFileName;

    private String stopTimesFileName = "stop_times.txt";
    private String stopTimesFullPath = dirOfGtfsFiles + stopTimesFileName;

    private String stopsFileName = "stops.txt";
    private String stopsFullPath = dirOfGtfsFiles + stopsFileName;

    private String calendarFileName = "calendar.txt";
    private String calendarFullPath = dirOfGtfsFiles + calendarFileName;

    private String makatFileName = "TripIdToDate.txt";
    private String makatFullPath = dirOfGtfsFiles + "../data/" + calendarFileName;

    protected final static Logger logger = LoggerFactory.getLogger("console");

    //public static ReadRoutesFileImpl gtfsFiles ;

    public Map<String, List<StopTimes>> stopTimesByTripId = new ConcurrentHashMap<>();
    private static List<String> cacheStopTimes = new LinkedList<>();
    public Map<String, Stop> stopsById = new HashMap<>();
    public Map<String, Stop> stopsByCode = new HashMap<>();
    public List<Stop> stops = new ArrayList<>();
    public List<Trip> allTrips = new ArrayList<>();
    public Map<String, Route> routesById = new ConcurrentHashMap<>();
    List<Calendar> allCalendars = new ArrayList<>();
    // map publishedName (such as "480") to list of routes
    public Map<String, List<Route>> routesByPublishedName = new ConcurrentHashMap<>();

    public Map<String, List<MakatData> > mapByRoute = new HashMap<>();
    public Map<String, MakatData> mapDepartueTimesOfRoute = new HashMap<>();

    @Autowired
    DataInit dataInit;

    @PostConstruct
    public void init() {
        logger.info("init in PostConstruct started");
        fullPath = dirOfGtfsFiles + fileName;
        tripsFullPath = dirOfGtfsFiles + tripsFileName;
        stopTimesFullPath = dirOfGtfsFiles + stopTimesFileName;
        stopsFullPath = dirOfGtfsFiles + stopsFileName;
        calendarFullPath = dirOfGtfsFiles + calendarFileName;
        makatFullPath = dirOfGtfsFiles + "../data/" + makatFileName;

        logger.warn("makatFile read starting");
        mapByRoute = readMakatFile();
        mapDepartueTimesOfRoute = processMapByRoute(mapByRoute);
//        logger.warn("15452: {}", mapDepartueTimesOfRoute.getOrDefault ("15452", new MakatData() ).toString());
//        logger.warn("19740: {}", mapDepartueTimesOfRoute.getOrDefault("19740", new MakatData()).toString());
//        logger.warn("15664: {}", mapDepartueTimesOfRoute.getOrDefault("15664", new MakatData()).toString());
        logger.warn("makatFile read done");

        cacheCalendars();
        initStops();
        cacheAllTrips();

        cacheRoutes();
        initializeRoutesByPublishedNameMap();

        // this will cache StopTimes, and init stopTimesByTripId
        //dataInit.initStopTimesByTripId(this);
        logger.info("init in PostConstruct completed");
    }

    private Map<String, MakatData> processMapByRoute(Map<String, List<MakatData>> mapByRoute) {
        // key is routeId
        Map<String, MakatData> mapDepartueTimesOfRoute = new HashMap<>();
        // find all makats
        for (String routeId : mapByRoute.keySet()) {
            Map<DayOfWeek, List<String>> departueTimesForDay = new HashMap<>();
            for (DayOfWeek day : DayOfWeek.values()) {
                departueTimesForDay.put(day, new ArrayList<>());
            }
            List<MakatData> linesOfRoute = mapByRoute.get(routeId);
            for (MakatData makatData : linesOfRoute) {
                departueTimesForDay.get(makatData.dayOfWeek).add(makatData.departure);
            }
            for (DayOfWeek day : DayOfWeek.values()) {
                departueTimesForDay.get(day).sort(Comparator.naturalOrder()); // sorts the list in-place
            }
            MakatData template = linesOfRoute.get(0);
            template.departureTimesForDay = departueTimesForDay;
            template.tripId = "";
            mapDepartueTimesOfRoute.put(routeId, template);
        }
        return mapDepartueTimesOfRoute;
    }

    private Map<String, List<MakatData> > readMakatFile() {
        List<String> lines = readAllLinesOfMakatFileAndDoItFast();
        if (lines.isEmpty()) return new HashMap<>();
        Map<String, List<MakatData> > mapByRoute =
            lines.stream().
                map(line -> parseMakatLine(line)).
                collect(Collectors.groupingBy(MakatData::getRouteId));
        return mapByRoute;
    }


    private MakatData parseMakatLine(String line) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
        String[] fields = line.split(",");
        String fromDate = fields[4];
        String toDate = fields[5];
        String dayInWeek = fields[7];
        MakatData makatData = new MakatData(
                fields[1],
                fields[0],
                fields[2],
                fields[3],
                LocalDateTime.parse(fromDate, formatter),
                LocalDateTime.parse(toDate, formatter),
                fields[6],
                dayFromNumber(dayInWeek),
                fields[8]
        );
        return makatData;
    }

    private DayOfWeek dayFromNumber(String num) {
        Map<String, DayOfWeek> days = new HashMap<>();
        days.put("1", DayOfWeek.SUNDAY);
        days.put("2", DayOfWeek.MONDAY);
        days.put("3", DayOfWeek.TUESDAY);
        days.put("4", DayOfWeek.WEDNESDAY);
        days.put("5", DayOfWeek.THURSDAY);
        days.put("6", DayOfWeek.FRIDAY);
        days.put("7", DayOfWeek.SATURDAY);
        return days.getOrDefault(num, DayOfWeek.SATURDAY);
    }

    private boolean doneOnce = false;
    private List<String> readAllLinesOfMakatFileAndDoItFast() {
        List<String> allLines = new ArrayList<>();
        if (doneOnce) return allLines;
        try{
            File inputF = new File(makatFullPath);
            InputStream inputFS = new FileInputStream(inputF);
            BufferedReader br = new BufferedReader(new InputStreamReader(inputFS));
            // skip the header of the csv
            allLines = br.lines().skip(1).collect(Collectors.toList());
            br.close();
        } catch (Exception e) {
            logger.error("", e);
        }
        doneOnce = true;
        return allLines;
    }

    private String updateProgress(int counter, int total) {
        String progress = Float.toString( Math.round (counter * 100.0 / total) ) ;
        if (progress.indexOf(".") > 0) {
            progress = progress.substring(0, progress.indexOf("."));
        }
        progress = progress + "%";
        if (counter % 1000 == 0) {
            logger.info("progress: {} ({}/{})", progress, counter, total);
        }
        return progress;
    }

    private void initOneTrip(Trip trip) {
        List<StopTimes> st = findStopTimesAtInit(trip.tripId);
        if ((st != null) && !st.isEmpty()) {
            stopTimesByTripId.put(trip.tripId, st);
        }
    }

    public List<StopTimes> findStopTimes(String tripId) {
        List<StopTimes> ret = stopTimesByTripId.get(tripId);
        if (ret == null) {
            for (Trip trip : allTrips.stream().filter(trip -> trip.tripId.equals(tripId)).collect(Collectors.toList())) {
                initOneTrip(trip);
            }
            return stopTimesByTripId.get(tripId);
        }
        else return ret;
    }
/*
    public static void main(String[] args)
    {
        // 415 BS-Jer 15527 6109
        // 416 BS-Jer 15529 6109
        // 417 BS-Jer (6660 6661 6662 12772 12773 12774) 3821
        // 418 BS-Jer (6670 6671 6673 12779 12780 16248) 3821
        // 418 BS-Jer 6672 3242
        // 419 BS-Jer 16067 3821
        // 420 BS-Jer 15531 6109
        ReadRoutesFileImpl rrf = new ReadRoutesFileImpl();
//        rrf.findTrips("15527");
        rrf.findRouteByPublishedName("15", Optional.of("בית שמש")).forEach(r -> logger.info(r.toString()) );
        //if (true) return;
        //List<Route> routeIds = rrf.findRouteByPublishedName("597", Optional.of("בית שמש"));
        //String routeId = "12774";   // 416
        List<String> routeIds = Arrays.asList("15541");
        for (String routeId : routeIds) {
            List<String> stopCodes = rrf.findLastStopCodeByRouteId(routeId);
            logger.info("stopCodes (last stop in route {}): {}", routeId, stopCodes);
        }
        rrf.findDepartueTime(rrf.findTripsById(routeIds.get(0)), DayOfWeek.SUNDAY);//LocalDateTime.now().getDayOfWeek().getValue());
    }
*/
    public List<String> findLastStopCodeByRouteId(String routeId) {
        return findLastStopCodeByRouteId(routeId, false);
    }

    public DepartureTimes findDeparturesByRouteId(String routeId) {
        List<Trip> trips = findTripsById(routeId);
        return findDepartureTime(trips, routeId);
    }
    @Cacheable("lastStopCodeOfRoute")
    public List<String> findLastStopCodeByRouteId(String routeId, boolean shortProcessing) {
        logger.info("find stopCodes (last stop in route {})", routeId);
        List<Trip> trips = findTripsById(routeId);
        if (shortProcessing) {
            logger.info("shortProcessing: will search only first trip");
            trips = Arrays.asList(trips.get(0));
        }
        Set<String> lastStopsInTrip = new HashSet<>();
        lastStopsInTrip = trips.
                stream().
                map(trip -> findLastStopIdOfTrip(trip.tripId)).
                map(stopTimes -> { System.out.print("+"); return stopTimes;}).
                map(stopTimes -> stopTimes.stopId).
                collect(Collectors.toSet());
        //rrf.findStopTimes("24155063_130117");
        lastStopsInTrip.forEach(stopId -> logger.info("stopId of last stop: {}", stopId));
        List<String> stopCodes = lastStopsInTrip.stream().map(stId -> findStopCode(stId)).collect(Collectors.toList());
        logger.info("stopCodes (last stop in route {}): {}", routeId, stopCodes);
        return stopCodes;
    }

//    private List<Trip> filterByDay(List<Trip> trips, DayOfWeek dayOfWeek) {
//        for (Trip trip : trips) {
//
//        }
//
//        return null;
//    }


    private void readAllLinesOfStopTimesFileAndDoItFast() {
        if (!cacheStopTimes.isEmpty()) return;
        try{
            File inputF = new File(stopTimesFullPath);
            InputStream inputFS = new FileInputStream(inputF);
            BufferedReader br = new BufferedReader(new InputStreamReader(inputFS));
            // skip the header of the csv
            cacheStopTimes = br.lines().skip(1).
                    //map(mapToItem).
                    collect(Collectors.toList());
            br.close();
        } catch (Exception e) {
            logger.error("", e);
        }
    }

    private Function<String, StopTimes> mapToItem = (line) -> {
        String[] p = line.split(",");// a CSV has comma separated lines
        //return new StopTimes("", "", "", "", 1,"", "", "");
        StopTimes item = parseStopTimesLine(line).get();
        return item;
    };


    public List<StopTimes> findStopTimesAtInit(String tripId) {
        try {
            if (cacheStopTimes.isEmpty()) {
                if (!(Paths.get(stopTimesFullPath).toFile().exists() &&
                        Paths.get(stopTimesFullPath).toFile().canRead())) {
                    logger.error("file {} does not exist or can't be read", stopTimesFullPath);
                    return new ArrayList<>();
                }
                logger.info("start");
                readAllLinesOfStopTimesFileAndDoItFast();
                //String str = new String(Files.readAllBytes(Paths.get(stopTimesFullPath)), StandardCharsets.UTF_8);
                logger.info("stop. all file in my cache!, size={}", cacheStopTimes.size());
            }
            List<StopTimes> stopTimes = cacheStopTimes.stream().
                    filter(line -> line.startsWith(tripId)).
                    map(mapToItem).
                    collect(Collectors.toList());
            return stopTimes;
        } catch (Exception e) {
            logger.error("", e);
            return new ArrayList<>();
        }
    }

    public StopTimes findLastStopIdOfTrip(String tripId) {
        logger.info("search stops for trip {}", tripId);
        List<StopTimes> stopTimes = findStopTimes(tripId);
        logger.info("found {} stopTimes", stopTimes.size());
        StopTimes lastStop = findLastStopInSequence(stopTimes);
        //logger.trace("tripId={}, lastStop: {}", tripId, lastStop);
        return lastStop;
    }

    public StopTimes findFirstStopIdOfTrip(String tripId) {
        List<StopTimes> stopTimes = findStopTimes(tripId);
        Optional<StopTimes> firstStop = findFirstStopInSequence(stopTimes);
        //logger.trace("tripId={}, firstStop: {}", tripId, lastStop);
        return firstStop.isPresent() ? firstStop.get() : null ;
    }

    private StopTimes findLastStopInSequence(List<StopTimes> stopTimes) {
        return stopTimes.
                stream().
                sorted((st1, st2) -> {return st2.stopSequence - st1.stopSequence;}).    // reversed order!!
                findFirst().
                get();
    }

    private Optional<StopTimes> findFirstStopInSequence(List<StopTimes> stopTimes) {
        return stopTimes.
                stream().
                sorted((st1, st2) -> {return st1.stopSequence - st2.stopSequence;}).
                findFirst();
    }

    private List<String> findDepartureTime(final Trip trip, final Set<String> serviceIds, final DayOfWeek dayOfWeek) {
        List<Calendar> calendars = getCalendars(serviceIds, dayOfWeek);
        List<String> departueTimes = Arrays.asList(trip)
                .stream().
                        filter(tr -> calendars.stream().anyMatch(c -> c.serviceId.equals(tr.serviceId))).
                        map(tr -> findFirstStopIdOfTrip(tr.tripId)).
                        map(st -> st.departureTime).
                        sorted().
                        collect(Collectors.toList());
        return departueTimes;
    }
    private DepartureTimes findDepartureTime(List<Trip> trips, String routeId) {
        DepartureTimes dt = new DepartureTimes(routeId, routesById.get(routeId).routeShortName);
        Set<String> serviceIds = trips.stream().map(trip -> trip.serviceId).collect(Collectors.toSet());
        for (DayOfWeek dayOfWeek : sortedWeekDays()) {
            for (Trip trip : trips) {
                List<Calendar> calendars = getCalendars(serviceIds, dayOfWeek);
                List<String> departureTimes = findDepartureTime(trip, serviceIds, dayOfWeek);
                dt.addDepartureTimes(dayOfWeek, departureTimes);
            }
        }
        for (DayOfWeek dayOfWeek : sortedWeekDays()) {
            Collections.sort(dt.departures.get(dayOfWeek));
            logger.info("departure times (on day {}): {}", dayOfWeek, dt.departures.get(dayOfWeek));
        }
        return dt;
    }

    private DayOfWeek[] sortedWeekDays() {
        return new DayOfWeek[] {
                DayOfWeek.SUNDAY,
                DayOfWeek.MONDAY,
                DayOfWeek.TUESDAY,
                DayOfWeek.WEDNESDAY,
                DayOfWeek.THURSDAY,
                DayOfWeek.FRIDAY,
                DayOfWeek.SATURDAY
        } ;
    }

    private boolean isDayOfWeek(Calendar c, DayOfWeek dayOfWeek) {
        switch (dayOfWeek) {
            case SUNDAY:    return c.sunday;
            case MONDAY:    return c.monday;
            case TUESDAY:   return c.tuesday;
            case WEDNESDAY: return c.wednesday;
            case THURSDAY:  return c.thursday;
            case FRIDAY:    return c.friday;
            case SATURDAY:  return c.saturday;
            default:        return false;
        }
    }

    public Stop findStopById(String stopId) {
        if (!(Paths.get(stopsFullPath).toFile().exists() &&
                Paths.get(stopsFullPath).toFile().canRead())) {
            logger.error("file {} does not exist or can't be read", stopsFullPath);
        }
        try {
            Stop stop = Files.
                    lines(Paths.get(stopsFullPath)).
                    map(ReadRoutesFileImpl::parseStopLine).
                    flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                    filter(st -> st.stopId.equals(stopId)).
                    collect(Collectors.toList()).get(0);
            //logger.debug("{}", stop);
            return stop;
        } catch (IOException ex) {
            logger.error("", ex);
            return null;
        }
    }

    public Stop findStopByCode(String stopCode) {
        if (!(Paths.get(stopsFullPath).toFile().exists() &&
                Paths.get(stopsFullPath).toFile().canRead())) {
            logger.error("file {} does not exist or can't be read", stopsFullPath);
        }
        try {
            Stop stop = Files.
                    lines(Paths.get(stopsFullPath)).
                    map(ReadRoutesFileImpl::parseStopLine).
                    flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                    filter(st -> st.stopCode.equals(stopCode)).
                    collect(Collectors.toList()).get(0);
            //logger.debug("{}", stop);
            return stop;
        } catch (IOException ex) {
            logger.error("", ex);
            return null;
        }
    }

    public String findStopCode(String stopId) {
        Stop stop = findStopById(stopId);
        logger.debug("{}", stop);
        return stop.stopCode;
    }


    private void cacheAllTrips() {
        if (!allTrips.isEmpty()) {
            return ;    // already cached
        }
        if (!(Paths.get(tripsFullPath).toFile().exists() &&
                Paths.get(tripsFullPath).toFile().canRead())) {
            logger.error("trips file {} does not exist or can't be read", tripsFullPath);
        }
        try {
            logger.info("started reading trips file");
            allTrips = Files.
                    lines(Paths.get(tripsFullPath)).
                    map(ReadRoutesFileImpl::parseTripsLine).
                    flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                    collect(Collectors.toList());
            //logger.debug("{}",trips.toString());//.replaceAll("},", "}\n").replace("[", "[\n "));
            logger.info("finished reading trips file");
        } catch (IOException ex) {
            logger.error("", ex);
        }

    }

    @Cacheable("tripsById")
    public List<Trip> findTripsById(String routeId) {
        cacheAllTrips();
        List<Trip> trips = allTrips.stream().
                    filter(trip -> trip.routeId.equals(routeId)).
                    collect(Collectors.toList());
        return trips;
    }

    private void cacheRoutes() {
        try {
            if (!routesById.isEmpty()) return ;

            Stream<String> stream = Files.lines(Paths.get(fullPath));

            List<Route> routes =
                    stream.
                            map(ReadRoutesFileImpl::parseLine).
                            flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                            collect(Collectors.toList());
            for (Route route : routes) {
                routesById.put(route.routeId, route);
            }
        } catch (IOException ex) {
            logger.error("", ex);
        }
        logger.info("init routesById completed, size={}", routesById.keySet().size());
    }

    public List<Route> findRouteByPublishedName(String linePublishedName, final Optional<String> cityInRouteName) {
        logger.trace("findRouteByPublishedName, linePublishedName={}, city={}", linePublishedName, cityInRouteName);
        List<Route> routes = routesById.values().stream().
                    filter(route -> route.routeShortName.equals(linePublishedName)).
                    filter (route -> {
                        if (cityInRouteName.isPresent()) {
                            return route.routeLongName.contains(cityInRouteName.get());
                        }
                        else return true;
                    } ).
                    collect(Collectors.toList());
        logger.trace("findRouteByPublishedName, return list of size {}", routes.size());
        return routes;
    }

    public Route findRouteById(String routeId) {
        cacheRoutes();
        return routesById.get(routeId);
    }

    private static Optional<Route> parseLine(String line) {
        if (StringUtils.isEmpty(line)) {
            return Optional.empty();
        }
        String[] ss = line.split(",");
        // route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_color
        Route r = new Route(ss[0], ss[1], ss[2], ss[3], ss[4]);
        // TODO route_type, route_color
        return Optional.of(r);
    }

    private static Optional<Trip> parseTripsLine(String line) {
        if (StringUtils.isEmpty(line)) {
            return Optional.empty();
        }
        String[] ss = line.split(",");
        // route_id,service_id,trip_id,direction_id,shape_id
        String shapeId = null;
        if (ss.length >= 5) {
            shapeId = ss[4];
        }
        Trip r = new Trip(ss[2], ss[1], ss[0], ss[3], shapeId);
        return Optional.of(r);
    }

    private static Optional<Stop> parseStopLine(String line) {
        if (StringUtils.isEmpty(line)) {
            return Optional.empty();
        }
        String[] ss = line.split(",");
        // stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,location_type,parent_station,zone_id
        String shapeId = null;
        if (ss.length >= 5) {
            shapeId = ss[4];
        }
        Stop r = new Stop(ss[0], ss[1], ss[2], ss[3], ss[4], ss[5]);
        return Optional.of(r);
    }

    private static Optional<StopTimes> parseStopTimesLine(String line) {
        if (StringUtils.isEmpty(line)) {
            return Optional.empty();
        }
        try {
            String[] ss = line.split(",");
            // trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type,shape_dist_traveled
            // 24043234_130117,14:20:00,14:20:00,36782,1,0,1,0
            StopTimes r = new StopTimes(ss[0], ss[1], ss[2], ss[3], Integer.parseInt(ss[4]), ss[5], ss[6], ss[7]);
            return Optional.of(r);
        }
        catch (Exception ex) {
            return Optional.empty();
        }
    }


    private static Optional<Calendar> parseCalendarLine(String line) {
        if (StringUtils.isEmpty(line)) {
            return Optional.empty();
        }
        try {
            String[] ss = line.split(",");
            // service_id,sunday,monday,tuesday,wednesday,thursday,friday,saturday,start_date,end_date
            // 42923424,0,0,0,0,0,1,0,20170113,20170314
            Calendar r = new Calendar(ss[0], ss[8], ss[9], "1".equals(ss[1]), "1".equals(ss[2]),
                    "1".equals( ss[3]), "1".equals( ss[4]), "1".equals( ss[5]),
                    "1".equals(ss[6]), "1".equals( ss[7]));
            return Optional.of(r);
        }
        catch (Exception ex) {
            return Optional.empty();
        }
    }


    public List<Calendar> getCalendars(Set<String> serviceIds, DayOfWeek dayOfWeek) {
        List<Calendar> calendars = new ArrayList<>();
        for (String serviceId : serviceIds) {
            List<Calendar> cals = getCalendar(serviceId, dayOfWeek);
            calendars.addAll(cals);
        }
        return  calendars;
    }


    private void cacheCalendars() {
        if (!allCalendars.isEmpty()) return;
        if (!(Paths.get(calendarFullPath).toFile().exists() &&
                Paths.get(calendarFullPath).toFile().canRead())) {
            logger.error("file {} does not exist or can't be read", calendarFullPath);
        }
        try {
            allCalendars = Files.
                    lines(Paths.get(calendarFullPath)).
                    map(ReadRoutesFileImpl::parseCalendarLine).
                    flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                    collect(Collectors.toList());
            //logger.debug("{}",cal.toString());//.replaceAll("},", "}\n").replace("[", "[\n "));
        } catch (IOException ex) {
            logger.error("", ex);
        }

    }
    public List<Calendar> getCalendar(String serviceId, DayOfWeek dayOfWeek) {
        cacheCalendars();
        List<Calendar> cal = allCalendars.stream().
                filter(calendar -> calendar.serviceId.equals(serviceId) && isDayOfWeek(calendar, dayOfWeek)).
                collect(Collectors.toList());
        //logger.debug("{}",cal.toString());//.replaceAll("},", "}\n").replace("[", "[\n "));
        return cal;
    }




    public void initializeRoutesByPublishedNameMap() {
        cacheRoutes();
        logger.info("init routesByPublishedName started");
        List<String> allPublishedNames =
            routesById.values().stream().
                map(route -> route.routeShortName).
                collect(Collectors.toList());
        for (String pName : allPublishedNames) {
            List<Route> routes = findRouteByPublishedName(pName, Optional.empty());
            if ((routes != null) && !routes.isEmpty()) {
                routesByPublishedName.put(pName, routes);
            }
        }
        logger.info("init routesByPublishedName completed");
    }


    private void initStops() {
        if (!(Paths.get(stopsFullPath).toFile().exists() &&
                Paths.get(stopsFullPath).toFile().canRead())) {
            logger.error("file {} does not exist or can't be read", stopsFullPath);
        }
        try {
            stops = Files.
                    lines(Paths.get(stopsFullPath)).
                    map(ReadRoutesFileImpl::parseStopLine).
                    flatMap(o -> o.isPresent() ? Stream.of(o.get()) : Stream.empty()).
                    map(stop -> {
                       stopsById.put(stop.stopId, stop);
                       stopsByCode.put(stop.stopCode, stop);
                       return stop;
                    }).
                    collect(Collectors.toList());
            //logger.debug("{}", stop);
        } catch (IOException ex) {
            logger.error("", ex);
        }
    }

    private class MakatData {
        public String makat = "";
        public String routeId;
        public String direction;
        public String alternative;
        public LocalDateTime fromDate;
        public LocalDateTime toDate;
        public String tripId;
        public DayOfWeek dayOfWeek;
        public String departure;
        public Map<DayOfWeek, List<String>> departureTimesForDay;

        public MakatData(String makat, String routeId, String direction, String alternative, LocalDateTime fromDate, LocalDateTime toDate, String tripId, DayOfWeek dayOfWeek, String departure) {
            this.makat = makat;
            this.routeId = routeId;
            this.direction = direction;
            this.alternative = alternative;
            this.fromDate = fromDate;
            this.toDate = toDate;
            this.tripId = tripId;
            this.dayOfWeek = dayOfWeek;
            this.departure = departure;
        }

        public MakatData() {
            new MakatData("", "", "", "", LocalDateTime.now(), LocalDateTime.now(), "", DayOfWeek.SATURDAY, "");
        }


        public String getRouteId() {
            return routeId;
        }

        @Override
        public String toString() {
            String s = "MakatData{" +
                    "makat='" + makat + '\'' +
                    ", routeId='" + routeId + '\'' +
                    ", direction='" + direction + '\'' +
                    ", alternative='" + alternative + '\'' +
                    ", fromDate=" + fromDate +
                    ", toDate=" + toDate +
                    ", tripId='" + tripId + '\'';
            if (departureTimesForDay == null) {
                s = s + ", dayOfWeek=" + dayOfWeek +
                        ", departure='" + departure + '\'' +
                        '}';
            }
            else {
                s = s + ", departures='" + departureTimesForDay.toString() + '\'' +
                        '}';
            }
            return s ;
        }
    }
}
