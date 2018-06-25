package org.hasadna.bus.service;

import ch.qos.logback.core.util.FixedDelay;
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
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
import java.io.IOException;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class ScheduleRetrieval {

    protected final Logger logger = LoggerFactory.getLogger(ScheduleRetrieval.class);

    @Value("${scheduler.default.interval.between.executions.minutes:3}")
    private int defaultTimeBetweenExecutionsOfSameCommandInMinutes ;

    @Value("${scheduler.data.file:/home/evyatar/logs/siri.schedule.json}")
    private String dataFileFullPath ;

    @Autowired
    SiriConsumeService siriConsumeService;

    @Autowired
    SiriProcessService siriProcessService;

    @Autowired
    SortedQueue queue;

    @PostConstruct
    public void init() {
        // hard coded for now
//        addScheduled("20594", "PT2H", "7023",7);    // line 480 Jer-TA
//        addScheduled("28627", "PT6H", "7453",7, 5);    // line 394 Eilat-TA
//        addScheduled("42978", "PT12H", "1559",7, 10);    // line 331 Nazaret-Haifa (working on Saturday?)
//        addScheduled("42734", "PT12H", "17177",7, 15);    // line 340 Nazaret-Haifa (working on Saturday?)
//        addScheduled("47210","PT12H","3792",7, 20); // line 40 Haifa (Saturday)
//        addScheduled("41048","PT2H","3701", 7, 25); // line 25 Haifa Saturday
//        addScheduled("41143","PT2H","3703", 7, 30); // line 25 Haifa Saturday (2nd direction)
//
//        // 415 Beit-Shemesh-Jer
//        addScheduled("6109", "PT2H", "8552", 7, 35);
//        //addScheduled("5195", "PT2H", "8555", 7);
//        addScheduled("6109", "PT2H", "15527", 7, 40);
//        //addScheduled("616", "PT2H", "15528", 7);

        List<Command> data = read();

        for (Command c : data) {
            queue.put(c);
        }

        logger.info("scheduler initialized.");
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

    public List<Command> read() {
        ObjectMapper mapper = new ObjectMapper();
        File file = Paths.get(dataFileFullPath).toFile();
        try {
            if (file.exists()) {
                SchedulingData data = mapper.readValue(file, SchedulingData.class);
                logger.info("read data: {}", data);
                List<Command> list = data.d;
                int counter = 0 ;
                int delayBeforeFirstInvocation = 4; // seconds
                if (list.size() > defaultTimeBetweenExecutionsOfSameCommandInMinutes * 60 / delayBeforeFirstInvocation) {
                    delayBeforeFirstInvocation = 1 ;
                }
                for (Command c : list) {
                    if (c.nextExecution == null) {
                        c.nextExecution = LocalDateTime.now().plusSeconds(counter);
                        counter = counter + delayBeforeFirstInvocation;
                    }
                }
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

//    @Scheduled(fixedDelay=120000)    // every 120 seconds
//    public void retrieve_480_Periodically() {
//        GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri("20594", "PT2H", "7023",7);
//        siriProcessService.process(result); // asynchronous invocation
//    }
//
//    @Scheduled(fixedDelay=295000)    // every 295 seconds
//    public void retrieve_394_Periodically() {
//        GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri("28627", "PT6H", "7453",7);
//        siriProcessService.process(result); // asynchronous invocation
//    }

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
    @Scheduled(fixedRate=100)    // every 100 ms.
    @Async("http-retrieve")
    public void retrieveCommandPeriodically() {
        //logger.trace("scheduled started");
        Command head = queue.peek();
        try {
            LocalDateTime now = LocalDateTime.now();
            //logger.trace("scheduling...");
            if (head.nextExecution.isAfter(now)) {
                //logger.trace("delaying {} until {} ...", head.lineRef, head.nextExecution);
                return;
            }
            Command c = queue.takeFromQueue();
            Command next = c.myClone();
            next.nextExecution = now.plusSeconds(next.executeEvery);
            queue.put(next);
            logger.trace("retrieving {} ...", c.lineRef);
            //GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri(c.stopCode, c.previewInterval, c.lineRef, c.maxStopVisits);
            GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri(c);
            siriProcessService.process(result); // asynchronous invocation
        }
        catch (Exception ex) {
            logger.error("absorbing unhandled exception", ex);
        }
    }
}
