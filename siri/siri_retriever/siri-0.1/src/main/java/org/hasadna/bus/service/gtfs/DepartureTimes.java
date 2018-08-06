package org.hasadna.bus.service.gtfs;

import java.time.DayOfWeek;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class DepartureTimes {

    public String routeId;
    public String publishedName;
    public Map<DayOfWeek, List<String>> departures = new ConcurrentHashMap<>();

    private DepartureTimes() {
    }

    public DepartureTimes(String routeId, String publishedName) {
        this.routeId = routeId;
        this.publishedName = publishedName;
        initMap();
    }

    private void initMap() {
        for (DayOfWeek dayOfWeek : sortedWeekDays()) {
            departures.put(dayOfWeek, new ArrayList<>());
        }
    }

    public void addDepartureTimes(DayOfWeek dayOfWeek, List<String> times) {
        List<String> deps = departures.get(dayOfWeek);
        if (deps == null) {
            departures.put(dayOfWeek, new ArrayList<>());
            deps = departures.get(dayOfWeek);
        }
        deps.addAll(times);
    }

    private DayOfWeek[] sortedWeekDays() {
        return new DayOfWeek[] {
                DayOfWeek.SUNDAY,
                DayOfWeek.MONDAY,
                DayOfWeek.TUESDAY,
                DayOfWeek.WEDNESDAY,
                DayOfWeek.THURSDAY,
                DayOfWeek.FRIDAY,
                DayOfWeek.SATURDAY
        } ;
    }
}
