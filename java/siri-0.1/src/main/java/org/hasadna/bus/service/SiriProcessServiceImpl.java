package org.hasadna.bus.service;

import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
public class SiriProcessServiceImpl implements SiriProcessService {

    protected final Logger logger = LoggerFactory.getLogger(SiriProcessServiceImpl.class);

    @Autowired
    SiriParseService siriParseService ;

    @Autowired
    SiriPersistService siriPersistService;

    @Override
    @Async("process-response")    // use a ThreadPool instead of the default SimpleAsync TaskExecutor
    public void process(GetStopMonitoringServiceResponse stopMonitorResult) {
        logger.info("async started");
        if (stopMonitorResult == null) {
            logger.trace("null response, no processing");
            return;
        }
        logger.info("processing...");
        Optional<String> summary = siriParseService.parseShortSummary(stopMonitorResult) ;
        // log to file
        summary.ifPresent(s ->
            siriPersistService.persistShortSummary(s));
        logger.info("processing...Done.");
    }
}
