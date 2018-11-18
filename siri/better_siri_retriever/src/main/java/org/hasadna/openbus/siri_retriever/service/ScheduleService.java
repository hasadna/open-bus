package org.hasadna.openbus.siri_retriever.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.hasadna.openbus.siri_retriever.entity.Command;
import org.hasadna.openbus.siri_retriever.entity.SchedulingData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.Clock;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class ScheduleService {

    protected final Logger logger = LoggerFactory.getLogger(ScheduleService.class);

    public static Clock DEFAULT_CLOCK = Clock.systemDefaultZone();

    @Value("${scheduler.default.interval.between.executions.minutes:3}")
    private int defaultTimeBetweenExecutionsOfSameCommandInMinutes ;

    @Value("${scheduler.enable:true}")
    boolean schedulerEnable;

    @Value("${scheduler.inactive.routes.mechanism.enabled:true}")
    boolean schedulerInactiveMechanismEnabled;

    @Value("${scheduler.data.file:/home/evyatar/logs/schedules/siri.schedule.3.Monday.json.2018-10-29}")
    public String dataFileFullPath ;


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
                LocalDateTime now = LocalDateTime.now(DEFAULT_CLOCK);
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

    private boolean match(final String name, final String pattern) {
        String prefix = pattern.split("\\*")[0];
        String suffix = pattern.split("\\*")[1];
        return name.startsWith(prefix) && name.endsWith(suffix);
    }

    private List<Command> unifyAllLists(List<List<Command>> all) {
        List<Command> list = new ArrayList<>();
        for (List<Command> each : all) {
            list.addAll(each);
        }
        return list;
    }

}
