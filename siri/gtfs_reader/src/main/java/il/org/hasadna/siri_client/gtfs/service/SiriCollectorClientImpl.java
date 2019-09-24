package il.org.hasadna.siri_client.gtfs.service;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;
import java.net.HttpURLConnection;
import java.net.URL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class SiriCollectorClientImpl implements SiriCollectorClient {
    private static Logger logger = LoggerFactory.getLogger(SiriCollectorClientImpl.class);

    @Override
    public int reschedule() {
        try {
            logger.info("calling API to reschedule all...");
            URL url = new URL(GtfsCollectorConfiguration.getRescheduleUrl());
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");
            int status = con.getResponseCode();
            logger.info(" ... Done. status = {}", status);

            return status;

        } catch (Exception e) {
            logger.error("calling API schedules/read/all failed", e);
            logger.trace("(this will cause another download of the GTFS in 15 minutes)");
            return 0;
        }
    }

}
