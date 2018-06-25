package org.hasadna.bus.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class SiriPersistFileService implements SiriPersistService {

    protected final Logger logger = LoggerFactory.getLogger(SiriPersistFileService.class);

    // this logger should be defined to a specific file
    protected final Logger fileLogger = LoggerFactory.getLogger("SiriRealTimeData");

    @Override
    public void persistShortSummary(String summary) {
        logger.info("persisting...");
        fileLogger.info(summary);
        logger.info("          ...Done");
    }
}
