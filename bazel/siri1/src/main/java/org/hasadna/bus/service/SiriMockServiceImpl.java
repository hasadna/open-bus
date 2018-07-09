package org.hasadna.bus.service;

import static java.nio.charset.StandardCharsets.UTF_8;

import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Profile;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

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
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import com.google.common.io.Resources;

@Component
@Profile("!production")
public class SiriMockServiceImpl implements SiriConsumeService {

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    final String SIRI_SERVICES_URL = "http://siri.motrealtime.co.il:8081/Siri/SiriServices";


    @Override
    public String retrieveFromSiri(String request) {
        return null;
    }

    @Override
    public String retrieveOneStop(String stopCode, String previewInterval, int maxStopVisits) {

        return null;
    }

// lineRef 19740 is 947

    @Override
    public String retrieveSpecificLineAndStop(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        if (lineRef.equals("7023")) {
            logger.info("reading 480-06.xml");
            return readFromFile("480-06");  // localhost:8080/data/oneStop/20594/7023/PT4H - 480 Jer-TA
        }
        else if (lineRef.equals("7453")) {
            logger.info("reading 394-01.xml");
            return readFromFile("394-01");  // localhost:8080/data/soap/oneStop/10331/7453/PT24H - 394 Eilat-TA
        }
        return readFromFile("480-01");
    }

    private String readFromFile(String name) {
        String fileName = "samples/" + name + ".xml";
        try {
            String content = Resources.toString(
                Resources.getResource(fileName), UTF_8);
            return content;
        } catch (IOException e) {
            logger.error("can't read file", e);
        }
        return null;
    }


    public GetStopMonitoringServiceResponse retrieveSiri(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        try {
            logger.info("retrieveSiri");
            String content = retrieveSpecificLineAndStop(stopCode, previewInterval, lineRef, maxStopVisits);

            JAXBContext jaxbContext = JAXBContext.newInstance(GetStopMonitoringServiceResponse.class);
            Unmarshaller jaxbUnmarshaller = jaxbContext.createUnmarshaller();
            StreamSource streamSource = new StreamSource(new StringReader(content));
            JAXBElement<GetStopMonitoringServiceResponse> je = jaxbUnmarshaller.unmarshal(streamSource, GetStopMonitoringServiceResponse.class);

            GetStopMonitoringServiceResponse response = (GetStopMonitoringServiceResponse)je.getValue();
            return response;

        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }



    private HttpHeaders createHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "text/xml; charset=utf-8");
        return headers;
    }

    private String generateTimestamp() {
        return LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME);
    }

    private String generateTimestamp(LocalDateTime ldt) {
        return ldt.format(DateTimeFormatter.ISO_DATE_TIME);
    }
}
