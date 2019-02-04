package org.hasadna.bus.service.gtfs;

import org.hasadna.bus.entity.gtfs.Trip;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class DataInit {

    protected final static Logger logger = LoggerFactory.getLogger("console");

    @Async
    public void initStopTimesByTripId(ReadRoutesFileImpl rrf) {
        int total = rrf.allTrips.size();
//        int counter = 0;
//        for (Trip trip : rrf.allTrips) {
//            counter = counter + 1 ;
//            updateProgress(counter, total);
//            initOneTrip(trip, rrf);
//        }
    }

    private String updateProgress(int counter, int total) {
        String progress = Float.toString( Math.round (counter * 100.0 / total) ) ;
        if (progress.indexOf(".") > 0) {
            progress = progress.substring(0, progress.indexOf("."));
        }
        progress = progress + "%";
        if (counter % 1000 == 0) {
            logger.info("progress: {} ({}/{})", progress, counter, total);
        }
        return progress;
    }

    private void initOneTrip(Trip trip, ReadRoutesFileImpl rrf) {
//        List<StopTimes> st = rrf.findStopTimesAtInit(trip.tripId);
//        if ((st != null) && !st.isEmpty()) {
//            rrf.stopTimesByTripId.put(trip.tripId, st);
//        }
    }
}
