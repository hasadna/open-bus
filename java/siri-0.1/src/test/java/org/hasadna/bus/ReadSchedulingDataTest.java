package org.hasadna.bus;

import org.assertj.core.api.Assertions;
import org.hasadna.bus.service.Command;
import org.hasadna.bus.service.ScheduleRetrieval;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.util.List;

@RunWith(SpringRunner.class)
@SpringBootTest
public class ReadSchedulingDataTest {

    @Autowired
    ScheduleRetrieval scheduleRetrieval;

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
        scheduleRetrieval.validateScheduling(list, LocalDateTime.now());
    }
}