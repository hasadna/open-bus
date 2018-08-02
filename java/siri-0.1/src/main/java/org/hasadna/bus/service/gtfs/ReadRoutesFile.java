package org.hasadna.bus.service.gtfs;

import org.hasadna.bus.entity.gtfs.Route;
import org.hasadna.bus.entity.gtfs.Stop;

import java.time.DayOfWeek;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public interface ReadRoutesFile {

    public Route findRouteById(String routeId);
    public List<String> findLastStopCodeByRouteId(String routeId, boolean shortProcessing);
    public DepartureTimes findDeparturesByRouteId(String routeId);
    public List<Route> findRouteByPublishedName(String linePublishedName, final Optional<String> cityInRouteName);
    public Stop findStopByCode(String stopCode);
    public Stop findStopById(String stopId);
    public boolean getStatus();
}
