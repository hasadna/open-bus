package org.hasadna.bus.service.gtfs;

import org.hasadna.bus.entity.gtfs.Route;
import org.hasadna.bus.entity.gtfs.Stop;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;

@Component
@Profile("notUsed")
public class ReadRoutesFileLeanImpl implements ReadRoutesFile {
    @Override
    public Route findRouteById(String routeId) {
        return null;
    }

    @Override
    public List<String> findLastStopCodeByRouteId(String routeId, boolean shortProcessing) {
        return null;
    }

    @Override
    public DepartureTimes findDeparturesByRouteId(String routeId) {
        return null;
    }

    @Override
    public List<Route> findRouteByPublishedName(String linePublishedName, Optional<String> cityInRouteName) {
        return null;
    }

    @Override
    public Stop findStopByCode(String stopCode) {
        return null;
    }

    @Override
    public Stop findStopById(String stopId) {
        return null;
    }
}
