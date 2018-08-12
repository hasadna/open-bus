package org.hasadna.bus;

import org.assertj.core.api.Assertions;
import org.hasadna.bus.service.Command;
import org.hasadna.bus.service.ScheduleRetrieval;
import org.hasadna.bus.util.DateTimeUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.PropertySource;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit4.SpringRunner;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;

@RunWith(SpringRunner.class)
@SpringBootTest
@TestPropertySource(locations="classpath:application-test.properties"
        ,properties = {"gtfs.dir.location=/home/evyatar/logs/" })
public class ReadSchedulingDataTest {

    private static final Logger logger = LoggerFactory.getLogger(ReadSchedulingDataTest.class);

    @Autowired
    ScheduleRetrieval scheduleRetrieval;

    @Test
    public void testLocalTime() {
        LocalTime x = LocalTime.of(23, 30) ;
        LocalTime y = x.plusMinutes(45);
        System.out.println(y.toString());
        Assertions.assertThat(y.isBefore(x)).isTrue();
    }

    @Test
    public void test1() {
        String file = this.getClass().getClassLoader().getResource("siri.schedule.18.Thursday.json").getFile();
        List<Command> list = scheduleRetrieval.readSchedulingData(file);
        Assertions.assertThat(list.size()).isGreaterThan(0);
        Command c1 = list.get(0);

        Assertions.assertThat(c1.lastArrivalTimes).isNotEmpty();
        Assertions.assertThat(c1.weeklyDepartureTimes.keySet().size()).isEqualTo(1);
        Assertions.assertThat(c1.weeklyDepartureTimes.keySet().iterator().next()).isEqualByComparingTo(DayOfWeek.THURSDAY);
    }

    @Test
    public void test2() {
        String file = this.getClass().getClassLoader().getResource("siri.schedule.18.Thursday.json").getFile();
        List<Command> list = scheduleRetrieval.readSchedulingData(file);
        scheduleRetrieval.addDepartures(list, LocalDate.now());
        logger.info("weeklyDepartureTimes {}", list.get(0).weeklyDepartureTimes );
        logger.info("departureTimes {}", list.get(0).departureTimes );
        logger.info("activeRanges {} to {}", list.get(0).activeRanges.get(0)[0], list.get(0).activeRanges.get(0)[1] );
        scheduleRetrieval.validateScheduling(list, LocalDateTime.of(2018, 8, 2, 20, 0));
    }
}