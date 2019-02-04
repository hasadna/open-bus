package org.hasadna.bus;

import org.assertj.core.api.Assertions;
import org.hasadna.bus.config.SchedulerConfig;
import org.hasadna.bus.service.Command;
import org.hasadna.bus.service.ScheduleRetrieval;
import org.hasadna.bus.service.SortedQueue;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.test.context.junit4.SpringRunner;

import java.time.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

import static org.hasadna.bus.util.DateTimeUtils.DEFAULT_CLOCK;
import static org.hasadna.bus.util.DateTimeUtils.timeAsStr;
import static org.hasadna.bus.util.DateTimeUtils.toDateTime;

@RunWith(SpringRunner.class)
@SpringBootTest //(classes = {SchedulerConfig.class, BusApplication.class})
public class ValidateSchedulingTest {

    @Autowired
    ScheduleRetrieval scheduleRetrieval;

    @Autowired
    SortedQueue sq;

    List<Command> data = new ArrayList<>();
    LocalDateTime currentTime;

    @Before
    public void setup() {

        currentTime = LocalDateTime.of(2018, 8, 7, 10, 0);
        DayOfWeek dayOfWeek = currentTime.getDayOfWeek();

        Command c = new Command("stopCode1");
        c.lineRef = "lineRef1";
        c.isActive = true;
        c.weeklyDepartureTimes = new HashMap<>();
        c.weeklyDepartureTimes.put(dayOfWeek, Arrays.asList("06:00", "07:00"));
        c.lastArrivalTimes = new HashMap<>();
        c.lastArrivalTimes.put(dayOfWeek, "09:00");
        data.add(c);

    }

    @Test
    public void test1() {

        ScheduleRetrieval.ValidationResults validationResults = scheduleRetrieval.validateScheduling(
                data,
                currentTime);

        Assertions.assertThat( validationResults.delayTillFirstDeparture ).isNotNull().isEmpty();
        Assertions.assertThat( validationResults.notNeeded).isNotNull().isNotEmpty();
        Assertions.assertThat( validationResults.notNeeded.get(0).stopCode).isEqualTo("stopCode1");
    }

    @Test
    public void test2() {

        currentTime = LocalDateTime.of(2018, 8, 7, 2, 0);
        ScheduleRetrieval.ValidationResults validationResults = scheduleRetrieval.validateScheduling(
                data,
                currentTime);

        Assertions.assertThat( validationResults.notNeeded ).isNotNull().isEmpty();
        Assertions.assertThat( validationResults.delayTillFirstDeparture).isNotNull().isNotEmpty();
        Assertions.assertThat( validationResults.delayTillFirstDeparture.get(0).stopCode).isEqualTo("stopCode1");
////        Assertions.assertThat( validationResults.delayTillFirstDeparture.get(0).nextExecution).isNotNull();
//        Assertions.assertThat( currentTime).isNotNull();
//        Assertions.assertThat( timeAsStr( currentTime.withHour(5).toLocalTime())).isEqualTo("05:00");
//        Assertions.assertThat( validationResults.delayTillFirstDeparture.get(0).nextExecution)
//                .isAfter(currentTime.withHour(5))
//                .isBefore(currentTime.withHour(6));
    }

    @Test
    public void test3() throws InterruptedException {
        currentTime = LocalDateTime.of(2018, 8, 7, 2, 0);
        DEFAULT_CLOCK = Clock.fixed(currentTime.toInstant(ZoneOffset.UTC), ZoneOffset.UTC);
        sq.removeAll();
        //System.out.println("a "+sq.getAllSchedules());
        data.forEach(c -> sq.put(c));

        //System.out.println("b "+sq.getAllSchedules());
        scheduleRetrieval.updateSchedulingDataPeriodically();
        Thread.sleep(2000); // updateScheduling happens in a different thread, so give it some time to happen
        //System.out.println("c "+sq.getAllSchedules());
        Assertions.assertThat(sq.getAllSchedules()).isNotNull().isNotEmpty();
        //System.out.println("1 "+sq.getAllSchedules());
        //List<Command> list = sq.getAllSchedules();
        Assertions.assertThat( currentTime).isNotNull();
        Assertions.assertThat( timeAsStr( currentTime.withHour(5).toLocalTime())).isEqualTo("05:00");
        //System.out.println("2 "+list);
        Assertions.assertThat(sq.getAllSchedules().get(0).nextExecution).isNotNull();
        //System.out.println("3 "+sq.getAllSchedules());
        Assertions.assertThat(sq.getAllSchedules().get(0).nextExecution).isNotNull();
        LocalDateTime ne = sq.getAllSchedules().get(0).nextExecution;
        LocalDateTime be = toDateTime("05:31", currentTime.toLocalDate());
        LocalDateTime af = toDateTime("05:29", currentTime.toLocalDate());
        Assertions.assertThat(ne)
                .isBefore(be)
                .isAfter(af);
//        Assertions.assertThat(sq.getAllSchedules().get(0).nextExecution)
//                .isBefore(toDateTime("05:31", currentTime.toLocalDate()))
//                .isAfter(toDateTime("05:29", currentTime.toLocalDate()));

    }

    @Test
    public void test4() throws InterruptedException {
        //currentTime = LocalDateTime.of(2018, 8, 7, 2, 0);
        DEFAULT_CLOCK =
                Clock.offset(Clock.systemDefaultZone(), Duration.ofHours(-55) );
                //Clock.fixed(Instant.parse("2018-04-29T10:15:30.00Z"),
                //        ZoneId.of("Asia/Calcutta"));
        //Clock myClock = DEFAULT_CLOCK;
        System.out.println(DEFAULT_CLOCK);
        currentTime = LocalDateTime.now(DEFAULT_CLOCK);
        System.out.println("now is " + currentTime.toString());

        while (currentTime.toString().equals("1")) {
            try {
                if (sq.getAll() == null) System.out.println("sq.getAll is null");
                System.out.println("" + LocalDateTime.now() + " queue:" + sq.getAll().length + ", active:" + sq.showActive().size());
                System.out.println(" next at:" + sq.peek().nextExecution.toLocalTime().toString());
            }
            catch ( Exception ex) {
                System.out.println("absorbing exception " + ex.getMessage());
            }
            Thread.sleep(10000);
        }
    }
}
