package org.hasadna.bus.service;

import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.hasadna.bus.service.gtfs.DepartureTimes;
import org.hasadna.bus.service.gtfs.ReadRoutesFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import javax.annotation.PostConstruct;
import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

import static org.hasadna.bus.util.DateTimeUtils.*;
import static org.hasadna.bus.util.DateTimeUtils.addMinutesStopAtMidnight;

@Component
public class ScheduleRetrieval {

    protected final Logger logger = LoggerFactory.getLogger(ScheduleRetrieval.class);

    @Value("${scheduler.default.interval.between.executions.minutes:3}")
    private int defaultTimeBetweenExecutionsOfSameCommandInMinutes ;

    @Value("${scheduler.enable:true}")
    boolean schedulerEnable;

    @Value("${scheduler.data.file:/home/evyatar/logs/siri.schedule.json}")
    private String dataFileFullPath ;

    @Autowired
    SiriConsumeService siriConsumeService;

    @Autowired
    SiriProcessService siriProcessService;

    @Autowired
    SortedQueue queue;

    @Autowired
    ReadRoutesFile makatFile ;




    @PostConstruct
    public void init() {
        List<Command> data = readSchedulingDataAllFiles(dataFileFullPath);
        addDepartures(data);
        // we currently don't filter out entries - only log warnings
        validateScheduling(data, LocalDateTime.now());

        for (Command c : data) {
            queue.put(c);
        }

        logger.info("scheduler initialized.");
    }

    // return false means - unschedule this command for the rest of the day
    // return true means - keep it scheduled
    private boolean checkNecessityOfThisSchedulingForRestOfToday(Command c, LocalDateTime currentTime, boolean disabled) {
        DayOfWeek today = currentTime.getDayOfWeek();

        if (!CollectionUtils.isEmpty(c.weeklyDepartureTimes) &&
                c.weeklyDepartureTimes.containsKey(today) &&
                !c.weeklyDepartureTimes.get(today).isEmpty()) {
            String firstDeparture = c.weeklyDepartureTimes.get(today).get(0);
            LocalDateTime timeOfFirstDeparture = toLocalTime(firstDeparture, currentTime);
            if (timeOfFirstDeparture.isAfter(currentTime.plusMinutes(30))) {
                // set nextExecution to 30 minutes before firstDeparture
                LocalDateTime nextExecution = timeOfFirstDeparture.minusMinutes(30);
                logger.info("route {} - postpone next execution to {}, firstDeparture only at {}", c.lineRef, nextExecution, timeOfFirstDeparture);
                return disabled; //notNeeded
            }
            LocalDateTime lastDeparture = toLocalTime(c.weeklyDepartureTimes.get(today).get(c.weeklyDepartureTimes.get(today).size() - 1), currentTime);
            String lastArrivalStr = "23:59";
            if (c.lastArrivalTimes != null) {
                lastArrivalStr = c.lastArrivalTimes.getOrDefault(today, "23:59");
            }
            if (lastArrivalStr.compareTo("23:59") > 0) lastArrivalStr = "23:59";
            LocalDateTime lastArrival = toLocalTime(lastArrivalStr, currentTime);
            if (currentTime.isAfter(lastDeparture)) {
                if (currentTime.isAfter(lastArrival.plusMinutes(30))) {
                    //stopQuerying
                    LocalDateTime nextExecution = LocalTime.of(23, 45).atDate(currentTime.toLocalDate());
                    logger.info("route {} - postpone next execution to {}, last Arrival will be at {}", c.lineRef, nextExecution, lastArrival);
                    return disabled; //notNeeded
                }
            }
            logger.info("route {} - not postponed! next execution {}, firstDeparture at {}", c.lineRef, c.nextExecution, timeOfFirstDeparture);

            logger.info("active range: {}", calculateActiveRanges(c.weeklyDepartureTimes, today, c.lastArrivalTimes));
        }
        else {
            logger.info("route {} - not postponed! next execution {}, weekly departure times unknown", c.lineRef, c.nextExecution);
        }
        return true;    // keep scheduling
    }

    public List<Command> validateScheduling(List<Command> data, LocalDateTime currentTime) {
        logger.info("validating ...");
        data = data.stream()
                .filter(c -> nextExecutionBefore2330(c))    // this will filter out those that their nextExecution was already changed
                //.filter(c -> !keepQuerying(c))
                .collect(Collectors.toList());
        // after filtering with NOT keepQuerying, what we have in data are
        // the Command objects that we do not need to query at all until the end of this day
        List<Command> notNeeded = new ArrayList<>();
        for (Command c : data) {
            if (false == checkNecessityOfThisSchedulingForRestOfToday(c, currentTime, true)) {
                notNeeded.add(c);
                // disabled = true means that this method will only log its result
            }

        }
        logger.debug("validateScheduling - return following routes that are not active any more today: {}", notNeeded.stream().map(c -> c.lineRef).collect(Collectors.toList()));
        return notNeeded;
    }

    private LocalDateTime toLocalTime(String departureTime, LocalDateTime currentTime) {
        try {
            String depTimeHourMinute = departureTime.substring(0, 5);
            if (depTimeHourMinute.compareTo("23:59") > 0) {
                depTimeHourMinute = "23:59";
            }
            return LocalTime.parse(depTimeHourMinute, DateTimeFormatter.ofPattern("HH:mm")).atDate(currentTime.toLocalDate());
        }
        catch (DateTimeParseException ex) {
            return LocalTime.of(23,59).atDate(currentTime.toLocalDate());
        }
    }

    private boolean nextExecutionBefore2330(Command c) {
        return
            (c.nextExecution != null) &&
                c.nextExecution.toLocalTime().isBefore(LocalTime.of(23, 30));

    }

    private boolean keepQuerying(Command c) {
        if (c == null) return true;
        String routeId = c.lineRef;
        try {
            boolean result = true;
            logger.debug("validating route {}", c.lineRef);
            DepartureTimes dt = makatFile.findDeparturesByRouteId(routeId);
            if (dt == null) {
                logger.warn("no departures found for route {}", routeId);
                return false;
            }
            List<String> departuesToday = dt.departures.get(LocalDateTime.now().getDayOfWeek());
            if (departuesToday.isEmpty()) {
                // today there are no departures for this route
                logger.warn("no departures on day {} for route {}", LocalDateTime.now().getDayOfWeek(), routeId);
                result = false;
            }
            String firstDeparture = departuesToday.stream().min(Comparator.naturalOrder()).orElse("00:00");
            String lastDeparture = departuesToday.stream().max(Comparator.naturalOrder()).orElse("23:59");
            if (LocalDateTime.now().toLocalTime().isBefore(
                    LocalTime.parse(firstDeparture, DateTimeFormatter.ofPattern("HH:mm")))) {
                logger.warn("route {} - first departure is only at {}", routeId, firstDeparture);
                result = true;  // though we could reduce frequency until time of first departure
            }
            // parsing last departure sometimes fails, because the hour is 24:15 or even 27:45
            // TODO handle these cases correctly
            if (LocalDateTime.now().toLocalTime().isAfter(
                    LocalTime.parse(lastDeparture, DateTimeFormatter.ofPattern("HH:mm")))) {
                logger.warn("route {} - No more departures today, last departure was at {}", routeId, lastDeparture);
                result = false;
            }
            return result;
        }
        catch (Exception ex) {
            logger.error("route {} - absorbing exception {}", routeId, ex.getMessage());
            return true;
        }
    }

    public void write() {
        ObjectMapper mapper = new ObjectMapper();
        ObjectWriter writer = mapper.writer(new DefaultPrettyPrinter());
        File file = Paths.get(dataFileFullPath).toFile();

        try {
            writer.writeValue(file, new SchedulingData(Arrays.asList(queue.getAll())));
            logger.info("data saved to file {}", dataFileFullPath);
        } catch (IOException e) {
            logger.error("error during writing data to file", e);
        }
    }

    public List<Command> readSchedulingDataAllFiles(String location) {
        if (Paths.get(location).toFile().isDirectory()) {
            // This is NOT a regex pattern
            // the match() method will split on the *
            // so we will read all files that start with "siri.schedule."
            // and end with ".json"
            String pattern = "siri.schedule.*.json";
            File[] ff = Paths.get(location).toFile().listFiles();
            List<File> files = Arrays.asList(ff);
            files.forEach(file -> logger.info("{},", file.getName()));
            files = files.stream().
                    filter(file -> !file.isDirectory() && match(file.getName(), pattern)).
                    collect(Collectors.toList());
            files.forEach(file -> logger.info("will read schedule file {},", file.getName()));
            return unifyAllLists(
                    files.stream().
                            map(file -> readSchedulingData(file.getAbsolutePath())).
                            collect(Collectors.toList()));
        }
        else {  // assuming it is a single file
            return readSchedulingData(location);
        }
    }

    private List<Command> unifyAllLists(List<List<Command>> all) {
        List<Command> list = new ArrayList<>();
        for (List<Command> each : all) {
            list.addAll(each);
        }
        return list;
    }

    // assume the pattern is always prefix*suffix
    private boolean match(final String name, final String pattern) {
        String prefix = pattern.split("\\*")[0];
        String suffix = pattern.split("\\*")[1];
        return name.startsWith(prefix) && name.endsWith(suffix);
    }

    public List<Command> readSchedulingData(String dataFile) {
        logger.info("read sheduling data from file {}", dataFile);
        ObjectMapper mapper = new ObjectMapper();
        File file = Paths.get(dataFile).toFile();
        try {
            if (file.exists() && !file.isDirectory() && file.canRead()) {
                SchedulingData data = mapper.readValue(file, SchedulingData.class);
                logger.debug("read data: {}", data);
                List<Command> list = data.data;
                int counter = 0 ;

                ///////////////////////
                // following part is to spread the scheduled invocations over several seconds, if possible
                int delayBeforeFirstInvocation = 4000; // ms
                if (list.size() > defaultTimeBetweenExecutionsOfSameCommandInMinutes * 60 * 1000 / delayBeforeFirstInvocation) {
                    delayBeforeFirstInvocation = 1000 ;
                }
                if (list.size() > 120) {
                    delayBeforeFirstInvocation = 120000 / list.size() ;
                }
                //
                ///////////////

                ///////////////////////////////////////
                // set the first value of nextExecution for each scheduled invocation
                LocalDateTime now = LocalDateTime.now();
                for (Command c : list) {
                    if (c.nextExecution == null) {
                        c.nextExecution = now.plus(counter, ChronoUnit.MILLIS);
                        counter = counter + delayBeforeFirstInvocation;
                    }
                }
                //
                ///////////////////
                logger.info("read {} entries from scheduling data file {}", list.size(), dataFileFullPath);
                return list;
            }
            else {
                logger.error("file {} does not exist", dataFileFullPath);
                return new ArrayList<>();
            }
        } catch (IOException e) {
            logger.error("error during reading data file", e);
        }
        return null;
    }


    public void addScheduled(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        queue.put(new Command(stopCode, previewInterval, lineRef, maxStopVisits, LocalDateTime.now(), defaultTimeBetweenExecutionsOfSameCommandInMinutes * 60));
        write();
    }

    public void addScheduled(String stopCode, String previewInterval, String lineRef, int maxStopVisits, int plusSeconds) {
        queue.put(new Command(stopCode, previewInterval, lineRef, maxStopVisits, LocalDateTime.now().plusSeconds(plusSeconds), defaultTimeBetweenExecutionsOfSameCommandInMinutes * 60));
        write();
    }

    public int removeScheduled(String lineRef) {
        if (StringUtils.isEmpty(lineRef)) return -1;
        List<Command> removed = queue.removeByLineRef(lineRef);
        write();
        return removed.size();
    }

    public List<String> findAll() {
        return queue.showAll();
    }

    public List<String> findActive() {
        return queue.showActive();
    }

    @Scheduled(fixedRate=30000)    // every 5 minutes.
    @Async
    public void updateSchedulingDataPeriodically() {
        try {
            // from validate we get list of all routeIds that will not depart any more TODAY.
            //addDepartures(data);
            List<String> notNeededToday =
                    validateScheduling(queue.getAllSchedules(), LocalDateTime.now())
                            .stream().map(c -> c.lineRef).collect(Collectors.toList());
            // so we change their nextExecute to about 23:45
            queue.stopQueryingToday(notNeededToday);
        }
        catch (Exception ex) {
            logger.error("absorbing exception when updating Scheduling Data. You should initiate re-read of all schedules", ex);
        }
    }


    /**
     * This method will execute every 100 ms.
     * It can execute in one of ${pool.http.retrieve.core.pool.size} threads.
     * If execution does not complete after 100 ms, the next execution will
     * happen in a different thread (if there is an available thread in the pool)
     *
     * Inside, the method takes the next task from the queue, and executes it
     * (but only if its "nextExecution" time has passed).
     * Before executing, it adds the same task again to the queue (with an updated
     * date for next execution)
     */
    @Scheduled(fixedRate=50)    // every 50 ms.
    @Async("http-retrieve")
    public void retrieveCommandPeriodically() {
        if (!schedulerEnable) return;
        //logger.trace("scheduled invocation started");
        Command head = queue.peek();
        try {
            LocalDateTime now = LocalDateTime.now();
            if (head.nextExecution.isAfter(now)) {
                //logger.trace("delaying {} until {} ...", head.lineRef, head.nextExecution);
                return;
            }
            Command c = queue.takeFromQueue();
            Command next = c.myClone();
            next.nextExecution = now.plusSeconds(next.executeEvery);
            queue.put(next);
            logger.trace("retrieving {} ...", c.lineRef);
            GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri(c);   // this part is synchronous
            logger.debug("retrieving {} ... done", c.lineRef);
            siriProcessService.process(result); // asynchronous invocation
        }
        catch (Exception ex) {
            //logger.error("absorbing unhandled exception", ex);
        }
    }


    // removing all entries, read again everything from schedule files
    // expect 4-10 seconds delay
    public void reReadSchedulingAndReplace() {
        logger.info("reading all schedules again");
        List<Command> data = readSchedulingDataAllFiles(dataFileFullPath);

        logger.info("{} schedules were read", data.size());

        addDepartures(data);

        // changes data by possibly setting nextExecution to a later time
        validateScheduling(data, LocalDateTime.now());

        // remove ALL current schedules
        logger.info("removing all schedules");
        queue.removeAll();

        // add the new schedules
        logger.info("inserting all new schedules");
        for (Command c : data) {
            queue.put(c);
        }

    }

    public void addDepartures(List<Command> allScheduledCommands) {
        try {
            if (makatFile != null && makatFile.getStatus()) {
                for (Command c : allScheduledCommands) {
                    DepartureTimes dt = makatFile.findDeparturesByRouteId(c.lineRef);
                    if (dt != null) {
                        c.weeklyDepartureTimes = dt.departures;
                        c.activeRanges = calculateActiveRanges(dt.departures, DayOfWeek.THURSDAY, c.lastArrivalTimes);
                    }
                }
                logger.info("departure times updated from makat file");
            }
        }
        catch (Exception ex) {
            logger.error("absorbing exception during readin from makatFile", ex);
        }
    }


    private List<LocalTime[]> calculateActiveRanges(Map<DayOfWeek, List<String>> departures, DayOfWeek dayOfWeek, Map<DayOfWeek, String> lastArrivals) {
        if (departures == null || departures.isEmpty())  {
            return Collections.emptyList();
        }
        if (!departures.containsKey(dayOfWeek) ||
                departures.get(dayOfWeek) == null ||
                departures.get(dayOfWeek).isEmpty()  ) {
            return listOfRanges("00:00", "23:59");
        }

        List<String> departuresToday = sorted(departures.get(dayOfWeek));

        // easiest solution: range from first to last
        LocalTime lastArrival = null;
        if (lastArrivals !=null && lastArrivals.containsKey(dayOfWeek)) {
            lastArrival = toTime(lastArrivals.get(dayOfWeek));
        }
        LocalTime rangeOpen = toTime(departuresToday.get(0)).minusMinutes(10);
        LocalTime rangeClose = toTime(addMinutesStopAtMidnight(departuresToday.get(departuresToday.size() - 1),60));
        if (lastArrival != null) {
            rangeClose = toTime( addMinutesStopAtMidnight(lastArrival,30) );
        }

        if (intervalInHoursRoundedUp(rangeOpen, rangeClose) >= 23) {
            return listOfRanges("00:00", "23:59");
        }
        else {
            return listOfRanges(rangeOpen, rangeClose);
        }
    }
}
