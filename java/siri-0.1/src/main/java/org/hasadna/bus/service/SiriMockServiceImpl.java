package org.hasadna.bus.service;

import io.micrometer.core.annotation.Timed;
import io.micrometer.core.instrument.*;
import io.micrometer.datadog.DatadogConfig;
import io.micrometer.datadog.DatadogMeterRegistry;
import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.context.annotation.Profile;
import org.springframework.core.env.Environment;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import uk.org.siri.siri.LineRefStructure;
import uk.org.siri.siri.MonitoredVehicleJourneyStructure;
import uk.org.siri.siri.NaturalLanguageStringStructure;

import static org.hasadna.bus.util.DateTimeUtils.DEFAULT_CLOCK;

import javax.annotation.PostConstruct;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;
import javax.xml.soap.MessageFactory;
import javax.xml.soap.SOAPException;
import javax.xml.soap.SOAPMessage;
import javax.xml.transform.stream.StreamSource;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.StringReader;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Clock;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.Random;
import java.util.concurrent.TimeUnit;

import static org.hasadna.bus.util.Util.removeSoapEnvelope;

@Component
@Profile("test")
public class SiriMockServiceImpl implements SiriConsumeService {

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    final String SIRI_SERVICES_URL = "http://siri.motrealtime.co.il:8081/Siri/SiriServices";

//    @Autowired
//    private DatadogMeterRegistry registry;

    @Autowired
    ReadFile readFile;

    @Override
    public GetStopMonitoringServiceResponse retrieveSiri(Command command) {

        if ("extended".equals(command.stopCode)) {
            invokeAccordingTo(command);
        }
        else {
            GetStopMonitoringServiceResponse result = null;
            //Timer.Sample sample = Timer.start(registry);

            // retrieve the data from siri
            result = retrieveSiri ( command.stopCode,
                                    command.previewInterval,
                                    command.lineRef,
                                    command.maxStopVisits);

            // measure response time, and log it to datadog with some tags
            //long latencyNano = sample.stop(registry.timer("mock.latency", "profile", "dev", "hour", Integer.toString(LocalTime.now().getHour())));
            //logger.trace("latency {} ms (0 -100 plus hour, so at 16:xx expecting average of 58", latencyNano / 1000000);

            return result;
        }
        return null;
    }

    private void invokeAccordingTo(Command command) {
        // currently we have only one "extended" implementation, so it is here
        try {
            int sleepTimeInMs = command.maxStopVisits * 1000 ;
            logger.info("start executing {}: sleep {} ms", command.description, sleepTimeInMs);
            Thread.sleep(sleepTimeInMs);
            logger.info("end sleep {} ms", sleepTimeInMs);
        } catch (InterruptedException e) {
            // absorb on purpose
        }
    }


    @Override
    public String retrieveFromSiri(String request) {
        return null;
    }

    @Override
    public String retrieveOneStop(String stopCode, String previewInterval, int maxStopVisits) {

        return null;
    }


    Random r = new Random();
    @Override
    public String retrieveSpecificLineAndStop(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {

        try {            Thread.sleep(r.nextInt(100) + LocalTime.now(DEFAULT_CLOCK).getHour());        } catch (InterruptedException e) {}

        if (lineRef.equals("7023")) {
            logger.trace("reading 480-06.xml");
            return readFromFile("480-06");  // localhost:8080/data/oneStop/20594/7023/PT4H - 480 Jer-TA
        }
        else if (lineRef.equals("7453")) {
            logger.trace("reading 394-01.xml");
            return readFromFile("394-01");  // localhost:8080/data/soap/oneStop/10331/7453/PT24H - 394 Eilat-TA
        }
        else if (lineRef.equals("10255")) {
            logger.trace("reading 59Jer-01.xml");
            return readFromFile("394-01");  // localhost:8080/data/soap/oneStop/10331/7453/PT24H - 394 Eilat-TA
        }
        logger.trace("reading 480-01.xml");
        return readFromFile("480-01");
    }

    private String readFromFile(String name) {
        return readFile.readFromFile(name);
    }

    private ThreadLocal<Unmarshaller> jaxbUnmarshaller = new ThreadLocal<>();

    public GetStopMonitoringServiceResponse retrieveSiri(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        try {
            logger.trace("retrieveSiri");
            String content = retrieveSpecificLineAndStop(stopCode, previewInterval, lineRef, maxStopVisits);
            //content = removeSoapEnvelope(content);
            logger.trace("xml retrieved, converting to response...");
            if (jaxbUnmarshaller.get() == null) {
                JAXBContext jaxbContext = JAXBContext.newInstance(GetStopMonitoringServiceResponse.class);
                Unmarshaller unmarshaller = jaxbContext.createUnmarshaller();
                jaxbUnmarshaller.set(unmarshaller);
            }
            StreamSource streamSource = new StreamSource(new StringReader(content));
            JAXBElement<GetStopMonitoringServiceResponse> je = jaxbUnmarshaller.get().unmarshal(streamSource, GetStopMonitoringServiceResponse.class);

            GetStopMonitoringServiceResponse response = (GetStopMonitoringServiceResponse)je.getValue();
            logger.trace("converting done");
            MonitoredVehicleJourneyStructure x =
            response.getAnswer().getStopMonitoringDelivery().
                    get(0).getMonitoredStopVisit().
                    get(0).getMonitoredVehicleJourney();
            NaturalLanguageStringStructure a = new NaturalLanguageStringStructure();
            a.setValue("420");
            x.setPublishedLineName(a);
            LineRefStructure b = new LineRefStructure();
            b.setValue("15531");
            x.setLineRef(b);
            return response;

        } catch (Exception e) {
            logger.error("absorbing unhandled", e);
        }

        return null;
    }



    private HttpHeaders createHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "text/xml; charset=utf-8");
        return headers;
    }

    private String generateTimestamp() {
        return LocalDateTime.now(DEFAULT_CLOCK).format(DateTimeFormatter.ISO_DATE_TIME);
    }

    private String generateTimestamp(LocalDateTime ldt) {
        return ldt.format(DateTimeFormatter.ISO_DATE_TIME);
    }
}
