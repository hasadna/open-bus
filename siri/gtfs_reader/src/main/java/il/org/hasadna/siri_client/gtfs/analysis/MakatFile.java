package il.org.hasadna.siri_client.gtfs.analysis;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class MakatFile {

    public String dirOfMakatFiles = "/tmp/";


    private String makatFileNamePrefix = "TripIdToDate";
    private String makatFileNameSuffix = ".txt";
    private String makatFullPath = null;    // initialized in init()

    protected final static Logger logger = LoggerFactory.getLogger("console");


    public Map<String, List<MakatData> > mapByRoute = new HashMap<>();
    public Map<String, MakatData> mapDepartureTimesOfRoute = new HashMap<>();

    boolean status = false;

    public void init(LocalDate date) {
        status = false;
        logger.info("init in PostConstruct started");
        if (!dirOfMakatFiles.endsWith("/")) {
            dirOfMakatFiles = dirOfMakatFiles + "/";
        }
        String makatFileName = makatFileNamePrefix + date.toString() + makatFileNameSuffix;
        makatFullPath = dirOfMakatFiles + makatFileName;

        try {
            logger.warn("makatFile read starting");
            mapByRoute = readMakatFile();
            if (mapByRoute.isEmpty()) {
                throw new IllegalArgumentException("makat file not found");
            }
            logger.info("makat file processing");
            LocalDate today = LocalDate.now();
            mapDepartureTimesOfRoute = processMapByRoute(mapByRoute, today);
            logger.warn("makatFile done");
            status = true;
        }
        catch (Exception ex) {
            logger.error("absorbing unhandled exception during reading makat file");
        }

        logger.info("init in PostConstruct completed");
    }

    public boolean getStatus() {
        return status;
    }

    private Map<String, MakatData> processMapByRoute(Map<String, List<MakatData>> mapByRoute, LocalDate startAtDate) {
        // key is routeId+date
        Map<String, MakatData> mapDepartureTimesOfRoute = new HashMap<>();
        // find all makats
        for (String routeId : mapByRoute.keySet()) {
            logger.trace("processing route {}", routeId);
            Map<LocalDate, List<String>> departureTimesForDate = new HashMap<>();
            for (int count = 0 ; count < 7 ; count++) {
                LocalDate date = startAtDate.plusDays(count);
                logger.trace("day {}, date {}, weekday {}", count, date, date.getDayOfWeek());
                departureTimesForDate.put(date, new ArrayList<>());
                List<MakatData> linesOfRoute = mapByRoute.get(routeId).stream()
                        .filter(makatData -> makatData.dayOfWeek.equals(date.getDayOfWeek()))
                        .filter(makatData -> !makatData.fromDate.isAfter(date) && !makatData.toDate.isBefore(date))
                        .collect(Collectors.toList());
                logger.trace("found {} records for route {}", linesOfRoute.size(), routeId);
                if (!linesOfRoute.isEmpty()) {
                    for (MakatData makatData : linesOfRoute) {
                        departureTimesForDate.get(date).add(makatData.departure);
                    }
                    departureTimesForDate.get(date).sort(Comparator.naturalOrder());
                    logger.trace("departureTimesForDate has {} departures", departureTimesForDate.get(date).size());
                    logger.trace("departures for date {}: {}", date, departureTimesForDate.get(date));
                    MakatData template = linesOfRoute.get(0);
                    template.departureTimesForDate = departureTimesForDate;
                    template.tripId = "";
                    String key = generateKey(routeId, date);
                    mapDepartureTimesOfRoute.put(key, template);
                    logger.trace("added to mapDepartureTimesOfRoute for key {}: {}", key, template);
                }
            }
        }
        return mapDepartureTimesOfRoute;
    }

    private String generateKey(String routeId, LocalDate date) {
        return routeId + "@" + date.toString();
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
                LocalDateTime.parse(fromDate, formatter).toLocalDate(),
                LocalDateTime.parse(toDate, formatter).toLocalDate(),
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

    public boolean doneOnce = false;
    private List<String> readAllLinesOfMakatFileAndDoItFast() {
        List<String> allLines = new ArrayList<>();
        if (doneOnce) return allLines;
        try{
            File inputF = new File(makatFullPath);
            if (!inputF.exists()) {
                logger.warn("file {} does not exist. return without data", makatFullPath);
                return allLines;
            }
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


    public Map<DayOfWeek, List<String>> findDeparturesByRouteId(String routeId, LocalDate date) {
        if ( (mapDepartureTimesOfRoute == null) || mapDepartureTimesOfRoute.isEmpty()) {
            return null;
        }
        if (routeId == null || routeId.equals("")) {
            return null;
        }
        MakatData md = mapDepartureTimesOfRoute.get(generateKey(routeId, date));
        if (md == null) {
            return null;
        }
        Map<DayOfWeek, List<String>> departures = new ConcurrentHashMap<>();
        for (LocalDate theDate : md.departureTimesForDate.keySet()) {
            departures.put(theDate.getDayOfWeek(), md.departureTimesForDate.get(theDate));
        }

        return departures;
    }



    private class MakatData {
        public String makat = "";
        public String routeId;
        public String direction;
        public String alternative;
        public LocalDate fromDate;
        public LocalDate toDate;
        public String tripId;
        public DayOfWeek dayOfWeek;
        public String departure;
        public Map<LocalDate, List<String>> departureTimesForDate;

        public MakatData(String makat, String routeId, String direction, String alternative, LocalDate fromDate, LocalDate toDate, String tripId, DayOfWeek dayOfWeek, String departure) {
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
            new MakatData("", "", "", "", LocalDate.now(), LocalDate.now(), "", DayOfWeek.SATURDAY, "");
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
            if (departureTimesForDate == null) {
                s = s + ", dayOfWeek=" + dayOfWeek +
                        ", departure='" + departure + '\'' +
                        '}';
            }
            else {
                s = s + ", departures='" + departureTimesForDate.toString() + '\'' +
                        '}';
            }
            return s ;
        }
    }
}
