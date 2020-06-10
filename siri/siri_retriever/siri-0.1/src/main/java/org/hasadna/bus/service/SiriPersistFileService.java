package org.hasadna.bus.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpEntity;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class SiriPersistFileService implements SiriPersistService {

    protected final Logger logger = LoggerFactory.getLogger(SiriPersistFileService.class);

    // this logger should be defined to a specific file - see logback.xml
    protected final Logger fileLogger = LoggerFactory.getLogger("SiriRealTimeData");

    @Value("${external.send:false}")
    boolean sendExternal;

    @Value("${external.url}")
    String url;

    @Autowired
    RestTemplateBuilder restTemplateBuilder;

    @Override
    public void persistShortSummary(String summary) {
        logger.trace("persisting...");
        fileLogger.info(summary);
        sendToExternal(summary);
        logger.trace("          ...Done");
    }
    
    private void sendToExternal(String str) {
        try {
            if (sendExternal && !StringUtils.isEmpty(str)) {
                restTemplateBuilder.build().postForEntity(url, new HttpEntity<String>(str, null), String.class);
            }
        }
        catch (Exception ex) {
            logger.debug("absorbing ", ex);
        }
        
    }
}

