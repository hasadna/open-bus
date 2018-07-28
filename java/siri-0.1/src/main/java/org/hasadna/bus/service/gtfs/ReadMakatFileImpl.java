package org.hasadna.bus.service.gtfs;

import org.hasadna.bus.entity.gtfs.Calendar;
import org.hasadna.bus.entity.gtfs.*;
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
@Profile({"production", "dev"})
public class ReadMakatFileImpl implements ReadRoutesFile {

    @Value("${gtfs.dir.location:/home/evyatar/work/hasadna/open-bus/gtfs/GTFS-2018-06-20/}")
    private String dirOfGtfsFiles ;


    private String makatFileName = "TripIdToDate.txt";
    private String makatFullPath = dirOfGtfsFiles + makatFileName;

    protected final static Logger logger = LoggerFactory.getLogger("console");


    public Map<String, List<MakatData> > mapByRoute = new HashMap<>();
    public Map<String, MakatData> mapDepartueTimesOfRoute = new HashMap<>();

    @Autowired
    DataInit dataInit;

    @PostConstruct
    public void init() {
        logger.info("init in PostConstruct started");
        if (!dirOfGtfsFiles.endsWith("/")) {
            dirOfGtfsFiles = dirOfGtfsFiles + "/";
        }
        makatFullPath = dirOfGtfsFiles + makatFileName;

        try {
            logger.warn("makatFile read starting");
            mapByRoute = readMakatFile();
            mapDepartueTimesOfRoute = processMapByRoute(mapByRoute);
            logger.warn("makatFile read done");
        }
        catch (Exception ex) {
            logger.error("absorbing unhandled exception during reading makat file");
        }

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
            logger.error("while trying to read makat file {}", makatFullPath, e);
            // handling - allLines will remain an empty list

            // such an exception usualy means that the file was not downloaded.
            // It will cause the periodic validation to not find departure times
            // because our current implementation takes them from makat file
            // (an alternative is to get them from GTFS files)
        }
        doneOnce = true;
        return allLines;
    }

    @Override
    public Route findRouteById(String routeId) {
        return null;
    }

    @Override
    public List<String> findLastStopCodeByRouteId(String routeId, boolean shortProcessing) {
        return null;
    }

    @Override
    public DepartureTimes findDeparturesByRouteId(String routeId) {
        if ( (mapDepartueTimesOfRoute == null) || mapDepartueTimesOfRoute.isEmpty()) {
            return null;
        }
        if (StringUtils.isEmpty(routeId)) {
            return null;
        }
        MakatData md = mapDepartueTimesOfRoute.get(routeId);
        if (md == null) {
            return null;
        }
        // TODO check if now is between fromDate and toDate

        DepartureTimes dt = new DepartureTimes(routeId, "");
        for (DayOfWeek day : md.departureTimesForDay.keySet()) {
            dt.addDepartureTimes(day, md.departureTimesForDay.get(day));
        }

        return dt;
    }

    @Override
    public List<Route> findRouteByPublishedName(String linePublishedName, Optional<String> cityInRouteName) {
        return null;
    }

    @Override
    public Stop findStopByCode(String stopCode) {
        return null;
    }

    @Override
    public Stop findStopById(String stopId) {
        return null;
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
