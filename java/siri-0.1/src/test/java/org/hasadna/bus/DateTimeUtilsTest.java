package org.hasadna.bus;


import org.assertj.core.api.Assertions;
import org.hasadna.bus.service.ScheduleRetrieval;
import org.junit.Test;

import java.time.*;
import java.util.*;

import static org.hasadna.bus.util.DateTimeUtils.*;

public class DateTimeUtilsTest {

    private LocalDateTime today = LocalDateTime.now(DEFAULT_CLOCK);
    private LocalDate TODAY = LocalDate.now(DEFAULT_CLOCK);


    @Test
    public void test1() {
        LocalDateTime x = toDateTime("21:05", TODAY);
        Assertions.assertThat(x.toLocalTime()).isEqualTo(LocalTime.of(21, 05));
        Assertions.assertThat(x.toLocalDate()).isEqualTo(TODAY);
    }

    @Test
    public void test2() {
        LocalDateTime x = toDateTime("24:05", TODAY);
        Assertions.assertThat(x.toLocalTime()).isEqualTo(LocalTime.of(0, 05));
        Assertions.assertThat(x.toLocalDate()).isEqualTo(TODAY.plusDays(1));
    }

    @Test
    public void test3() {
        LocalDateTime x = toDateTime("00:05", TODAY);
        Assertions.assertThat(x.toLocalTime()).isEqualTo(LocalTime.of(0, 05));
        Assertions.assertThat(x.toLocalDate()).isEqualTo(TODAY);
        LocalDateTime y = x.minusMinutes(10);
        Assertions.assertThat(y.toLocalTime()).isEqualTo(LocalTime.of(23, 55));
        Assertions.assertThat(y.toLocalDate()).isEqualTo(TODAY.minusDays(1));

        Assertions.assertThat(subtractMinutesStopAtMidnight("00:05", 10)).isEqualTo("00:00");
        Assertions.assertThat(addMinutesStopAtMidnight("23:45", 20)).isEqualTo("23:59");
    }

    @Test
    public void test4() {
        int diff = intervalInHoursRoundedUp("00:00", "03:55");
        Assertions.assertThat(diff).isEqualTo(4);

        diff = intervalInHoursRoundedUp("09:00", "10:55");
        //should be 2
        Assertions.assertThat(diff).isEqualTo(2);
    }

    @Test
    public void test5() {
        LocalDateTime early = LocalDateTime.now(DEFAULT_CLOCK).withHour(10).withMinute(0);
        LocalDateTime late = LocalDateTime.now(DEFAULT_CLOCK).withHour(12).withMinute(0);
        long diff = Duration.between(early, late).toMinutes();
        Assertions.assertThat(diff).isGreaterThan(0).isEqualTo(120);

        long negativeDiff = Duration.between(late, early).toMinutes();
        //Assertions.assertThat(diff).isLessThan(0);  // it is NOT! Duration.between is the absolute value of the time difference
        Assertions.assertThat(Duration.between(late, early).isNegative());
    }

    @Test
    public void test6() {
        Map<DayOfWeek, List<String>> departuresOnSunday = new HashMap<>();
        departuresOnSunday.put(DayOfWeek.SUNDAY,Arrays.asList("10:00", "12:30"));
        Map<DayOfWeek, String> lastArrivals = new HashMap<>();
        lastArrivals.put(DayOfWeek.SUNDAY, "13:00");
        List<LocalTime[]> ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("09:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("13:30")); // 30 minutes after last arrival

        lastArrivals.remove(DayOfWeek.SUNDAY);
        ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("09:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("13:30")); // no lastArrival! so 60 minutes after last departure!

    }


    @Test
    public void test7() {
        Map<DayOfWeek, List<String>> departuresOnSunday = new HashMap<>();
        departuresOnSunday.put(DayOfWeek.SUNDAY,Arrays.asList("05:00", "07:30", "10:00", "12:30", "15:00", "17:30", "20:00"));
        Map<DayOfWeek, String> lastArrivals = new HashMap<>();
        lastArrivals.put(DayOfWeek.SUNDAY, "20:45");
        List<LocalTime[]> ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("04:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("21:15")); // 30 minutes after last arrival

        lastArrivals.remove(DayOfWeek.SUNDAY);
        ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("04:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("21:00")); // no lastArrival! so 60 minutes after last departure!

    }


    @Test
    public void test8() {
        Map<DayOfWeek, List<String>> departuresOnSunday = new HashMap<>();
        departuresOnSunday.put(DayOfWeek.SUNDAY,Arrays.asList("05:00", "07:30", "10:00", "12:30", "15:00", "17:30", "20:00", "23:10"));
        Map<DayOfWeek, String> lastArrivals = new HashMap<>();
        lastArrivals.put(DayOfWeek.SUNDAY, "23:55");
        List<LocalTime[]> ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("04:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("23:59")); // 30 minutes after last arrival

        lastArrivals.remove(DayOfWeek.SUNDAY);
        ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("04:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("23:59")); // no lastArrival! so 60 minutes after last departure!

    }

    @Test
    public void test9() {
        Map<DayOfWeek, List<String>> departuresOnSunday = new HashMap<>();
        departuresOnSunday.put(DayOfWeek.SUNDAY,Arrays.asList("05:00", "07:30", "10:00", "12:30", "15:00", "17:30", "20:00", "23:10"));
        Map<DayOfWeek, String> lastArrivals = new HashMap<>();
        lastArrivals.put(DayOfWeek.SUNDAY, "24:05");
        List<LocalTime[]> ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("04:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("23:59")); // 30 minutes after last arrival

        lastArrivals.remove(DayOfWeek.SUNDAY);
        ranges = new ScheduleRetrieval()
                .calculateActiveRanges(departuresOnSunday, DayOfWeek.SUNDAY, lastArrivals);
        Assertions.assertThat(ranges.get(0)[0]).isEqualTo(toTime("04:50"));  // 10 minutes before first departure
        Assertions.assertThat(ranges.get(0)[1]).isEqualTo(toTime("23:59")); // no lastArrival! so 60 minutes after last departure!

    }

    @Test
    public void test10() {
        LocalDateTime fixed = fixTimeStrAfterMidnight("23:00", LocalDate.now(DEFAULT_CLOCK));
        Assertions.assertThat(timeAsStr(fixed)).isEqualTo("23:00");
        fixed = fixTimeStrAfterMidnight("24:05", LocalDate.now(DEFAULT_CLOCK));
        Assertions.assertThat(timeAsStr(fixed)).isEqualTo("00:05");

        String hour = upperBoundTimeStrAfterMidnight("23:30");
        Assertions.assertThat(hour).isEqualTo("23:30");
        hour = upperBoundTimeStrAfterMidnight("24:05");
        Assertions.assertThat(hour).isEqualTo("23:59");
    }
}
