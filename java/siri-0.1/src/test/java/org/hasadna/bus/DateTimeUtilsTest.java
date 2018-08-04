package org.hasadna.bus;


import org.assertj.core.api.Assertions;
import org.junit.Test;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;

import static org.hasadna.bus.util.DateTimeUtils.*;

public class DateTimeUtilsTest {

    private LocalDateTime today = LocalDateTime.now();
    private LocalDate TODAY = LocalDate.now();


    @Test
    public void test1() {
        LocalDateTime x = toDateTime("21:05", TODAY);
        Assertions.assertThat(x.toLocalTime()).isEqualTo(LocalTime.of(21, 05));
        Assertions.assertThat(x.toLocalDate()).isEqualTo(TODAY);
    }

    @Test
    public void test2() {
        LocalDateTime x = toDateTime("24:05", TODAY);
        Assertions.assertThat(x.toLocalTime()).isEqualTo(LocalTime.of(21, 05));
        Assertions.assertThat(x.toLocalDate()).isEqualTo(TODAY);
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
}
