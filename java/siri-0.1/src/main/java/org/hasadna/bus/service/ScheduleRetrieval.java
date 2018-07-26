package org.hasadna.bus.service;

import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import io.micrometer.core.annotation.Timed;
import io.micrometer.core.instrument.Tags;
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
import org.springframework.util.StringUtils;

import javax.annotation.PostConstruct;
import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalUnit;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

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

        // we currently don't filter out entries - only log warnings
        validateScheduling(data);

        for (Command c : data) {
            queue.put(c);
        }



        logger.info("scheduler initialized.");
    }

    private List<Command> validateScheduling(List<Command> data) {
        logger.info("validating ...");
        data = data.stream().filter(c -> {
            try {
                boolean result = true;
                logger.info("validating route {}", c.lineRef);
                String routeId = c.lineRef;
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
                    result = false;
                }
                if (LocalDateTime.now().toLocalTime().isAfter(
                        LocalTime.parse(lastDeparture, DateTimeFormatter.ofPattern("HH:mm")))) {
                    logger.warn("route {} - No more departures today, last departure was at {}", routeId, lastDeparture);
                    result = false;
                }
                return result;
            }
            catch (Exception ex) {
                logger.error("absorbing exception {}", ex.getMessage());
                return true;
            }
        }).collect(Collectors.toList());
        return data;
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
            String pattern = "siri\\.schedule\\..*json";
            File[] ff = Paths.get(location).toFile().listFiles();
            List<File> files = Arrays.asList(ff);
            files.forEach(file -> logger.info("{},", file.getName()));
            files = files.stream().
                    filter(file -> !file.isDirectory() && match(file.getName(), pattern)).
                    collect(Collectors.toList());
            files.forEach(file -> logger.info("{},", file.getName()));
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

    private boolean match(final String name, final String literal) {
        Pattern pattern = Pattern.compile(literal);
        Matcher matcher = pattern.matcher(name);
        return matcher.find();
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


    @Scheduled(fixedRate=300000)    // every 5 minutes.
    @Async
    //@Timed("validate")
    public void updateSchedulingDataPeriodically() {
        // hopefully validate won't change the data from inside...
        validateScheduling(queue.getAllSchedules());
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
        logger.trace("scheduled invocation started");
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
            logger.info("retrieving {} ...", c.lineRef);
            GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri(c);   // this part is synchronous
            logger.info("retrieving {} ... done", c.lineRef);
            siriProcessService.process(result); // asynchronous invocation
        }
        catch (Exception ex) {
            logger.error("absorbing unhandled exception", ex);
        }
    }


    // removing all entries, read again everything from schedule files
    // expect 4-10 seconds delay
    public void reReadSchedulingAndReplace() {
        logger.info("reading all schedules again");
        List<Command> data = readSchedulingDataAllFiles(dataFileFullPath);

        logger.info("{} schedules were read", data.size());

        // we currently don't filter out entries - only log warnings
        validateScheduling(data);

        // remove ALL current schedules
        logger.info("removing all schedules");
        queue.removeAll();

        // add the new schedules
        logger.info("inserting all new schedules");
        for (Command c : data) {
            queue.put(c);
        }

    }
}
