package org.hasadna.bus.util;

import org.hasadna.bus.service.ScheduleRetrieval;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class DateTimeUtils {

    private static final Logger logger = LoggerFactory.getLogger(DateTimeUtils.class);

    public static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm");
    public static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    public static final String START_OF_DAY = "00:00";
    public static final String END_OF_DAY = "23:59";
    public static final LocalTime END_OF_DAY_AS_TIME = toTime(END_OF_DAY);

    public static LocalDateTime toDateTime(String hourAsStr, LocalDate atDate) {
        // hourAsStr is of the format HH:mm
        try {
            return LocalTime.parse(hourAsStr, TIME_FORMAT).atDate(atDate);
        } catch (DateTimeParseException ex) {
            // assuming this is because the hour is 24:xx or 25:xx
            int hour = Integer.parseInt(hourAsStr.split(":")[0]);
            int minutes = Integer.parseInt(hourAsStr.split(":")[1]);
            hour = hour - 24;
            LocalDate tomorrow = atDate.plusDays(1);
            return LocalTime.of(hour, minutes).atDate(tomorrow);
        }
    }

    public static LocalDateTime toDateTime(String hourAsStr) {
        return toDateTime(hourAsStr, LocalDate.now());
    }

    public static LocalTime toTime(String hourAsStr) {
        if (hourAsStr.length() == 8 && hourAsStr.lastIndexOf(':') == 5) {
            hourAsStr = hourAsStr.substring(0, 5);
        }

        // hourAsStr is of the format HH:mm
        return LocalTime.parse(hourAsStr, TIME_FORMAT);
    }

    public static LocalDate toDate(String dateStr) {
        return LocalDate.parse(dateStr, DATE_FORMAT);
    }

    public static String timeAsStr(LocalTime time) {
        return time.format(TIME_FORMAT);
    }

    public static String timeAsStr(final LocalDateTime dateTime) {
        return dateTime.format(TIME_FORMAT);
    }

    // "21:05" plus 30 will be "21:35"
    // "23:15" plus 50 will be "23:59"
    public static String addMinutesStopAtMidnight(String timeAsStr, int minutesToAdd) {
        LocalDateTime original = toDateTime(timeAsStr, LocalDate.now());
        LocalDateTime theDateTime = original.plusMinutes(minutesToAdd);
        if (theDateTime.getDayOfYear() != original.getDayOfYear()) {
            return END_OF_DAY;
        }
        return timeAsStr(theDateTime);
    }

    public static String addMinutesStopAtMidnight(LocalTime time, int minutesToAdd) {
        return addMinutesStopAtMidnight(timeAsStr(time), minutesToAdd);
    }


    public static String subtractMinutesStopAtMidnight(String timeAsStr, int minutesToSubtruct) {
        LocalDateTime original = toDateTime(timeAsStr, LocalDate.now());
        LocalDateTime theDateTime = original.minusMinutes(minutesToSubtruct);
        if (theDateTime.getDayOfYear() != original.getDayOfYear()) {
            return START_OF_DAY;
        }
        return timeAsStr(theDateTime);
    }


    public static List<LocalTime[]> listOfRanges(String start, String end) {
        return listOfRanges(toTime(start), toTime(end));
    }

    public static List<LocalTime[]> listOfRanges(LocalTime start, LocalTime end) {
        List<LocalTime[]> list = new ArrayList<>();
        list.add(new LocalTime[]{start, end});
        return list;
    }

    // changes the list that was given as the argument to be sorted
    public static void sortTimesInTheSameList(List<String> times) {
        times.sort(String::compareTo);
    }

    public static List<String> sorted(List<String> list) {
        List<String> newList = new ArrayList<>();
        newList.addAll(list);
        newList.sort(String::compareTo);
        return newList;
    }

    public static int intervalInHoursRoundedUp(String rangeOpen, String rangeClose) {
        return intervalInHoursRoundedUp(toTime(rangeOpen), toTime(rangeClose));
    }

    public static int intervalInHoursRoundedUp(LocalTime rangeOpen, LocalTime rangeClose) {
        long diff = Duration.between(rangeOpen, rangeClose).toHours();
        return 1 + Long.valueOf(diff).intValue();   // we round up instead of down (diff between 09:00 and 10:55 should be 2)
    }

}