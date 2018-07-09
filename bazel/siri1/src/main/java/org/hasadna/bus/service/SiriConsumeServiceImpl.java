package org.hasadna.bus.service;

import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.util.StopWatch;
import org.springframework.web.client.RestTemplate;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;
import javax.xml.soap.SOAPMessage;
import javax.xml.transform.stream.StreamSource;
import java.io.StringReader;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.stream.IntStream;

@Component
@Profile("production")
public class SiriConsumeServiceImpl implements SiriConsumeService {

    @Value("${number.of.intervals:12}")
    int numberOfIntervals ;

    @Value("${duration.of.interval.in.minutes:5}")
    int durationOfIntervalInMinutes ;

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    final String SIRI_SERVICES_URL = "http://siri.motrealtime.co.il:8081/Siri/SiriServices";

    @Override
    public GetStopMonitoringServiceResponse retrieveSiri(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        StopWatch sw1 = new StopWatch(Thread.currentThread().getName());
        sw1.start();
        logger.info("retrieving... {}", lineRef);
        String content = retrieveSpecificLineAndStop(stopCode, previewInterval, lineRef, maxStopVisits);
        sw1.stop();
        logger.info("retrieving...Done ({} ms)", sw1.getTotalTimeMillis());
        logger.debug("lineRef={}, stopCode={}, previewInterval={}, response={}", lineRef, stopCode, previewInterval, content);

        StopWatch sw2 = new StopWatch(Thread.currentThread().getName());
        sw2.start();

        content = removeSoapEnvelope(content);
        logger.trace(content);

        //unmarshall XML to object
        GetStopMonitoringServiceResponse response = unmarshalXml(content);

        sw2.stop();
        logger.info("unmarshal to POJO: {} ms", sw2.getTotalTimeMillis());

        return response;
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

    // A thread local construct to re-use jaxb unmarshallers
    // because their creation time is very long. So we keep one unmarshaller per thread.
    ThreadLocal<Unmarshaller> localUnmarshaller = ThreadLocal.withInitial(() -> {
        try {
            JAXBContext jaxbContext = JAXBContext.newInstance(GetStopMonitoringServiceResponse.class);
            Unmarshaller jaxbUnmarshaller = jaxbContext.createUnmarshaller();
            return jaxbUnmarshaller;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    });



    @Override
    public String retrieveSpecificLineAndStop(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        String url = SIRI_SERVICES_URL;
        String requestXmlString = buildServiceRequest(stopCode, previewInterval, lineRef, maxStopVisits);
        HttpEntity<String> entity = new HttpEntity<String>(requestXmlString, createHeaders());

        // measure time
        StopWatch sw = new StopWatch(Thread.currentThread().getName());
        sw.start();

        RestTemplate restTemplate = new RestTemplate();
        logger.trace(requestXmlString);
        ResponseEntity<String> r = restTemplate.postForEntity(url, entity, String.class);

        sw.stop();
        logger.info("network to MOT server: {} ms", sw.getTotalTimeMillis());

        logger.trace("status={}", r.getStatusCode());
        logger.trace("statusCodeValue={}", r.getStatusCodeValue());
        logger.trace(r.getBody());
        return r.getBody();
    }


    final String sampleRequestXml = "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"\n" +
            "                   xmlns:SOAP-ENC=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:acsb=\"http://www.ifopt.org.uk/acsb\"\n" +
            "                   xmlns:datex2=\"http://datex2.eu/schema/1_0/1_0\" xmlns:ifopt=\"http://www.ifopt.org.uk/ifopt\"\n" +
            "                   xmlns:siri=\"http://www.siri.org.uk/siri\" xmlns:siriWS=\"http://new.webservice.namespace\"\n" +
            "                   xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n" +
            "                   xsi:schemaLocation=\"http://192.241.154.128/static/siri/siri.xsd\">\n" +
            "    <SOAP-ENV:Header/>\n" +
            "    <SOAP-ENV:Body>\n" +
            "        <siriWS:GetStopMonitoringService>\n" +
            "            <Request xsi:type=\"siri:ServiceRequestStructure\">\n" +
            "                <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
            "                <siri:RequestorRef xsi:type=\"siri:ParticipantRefStructure\">ML909091</siri:RequestorRef>\n" +
            "                <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\">0100700:1351669188:4684</siri:MessageIdentifier>\n" +
            "                <siri:StopMonitoringRequest version=\"IL2.7\" xsi:type=\"siri:StopMonitoringRequestStructure\">\n" +
            "                    <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
            "                    <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\"></siri:MessageIdentifier>\n" +
            "                    <siri:PreviewInterval>PT60M</siri:PreviewInterval>\n" +
            "                    <siri:MonitoringRef xsi:type=\"siri:MonitoringRefStructure\">42658</siri:MonitoringRef>\n" +
            "                    <siri:MaximumStopVisits>1000</siri:MaximumStopVisits>\n" +
            "                </siri:StopMonitoringRequest>\n" +
            "                <siri:StopMonitoringRequest version=\"IL2.7\" xsi:type=\"siri:StopMonitoringRequestStructure\">\n" +
            "                    <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
            "                    <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\"></siri:MessageIdentifier>\n" +
            "                    <siri:PreviewInterval>PT60M</siri:PreviewInterval>\n" +
            "                    <siri:MonitoringRef xsi:type=\"siri:MonitoringRefStructure\">42684</siri:MonitoringRef>\n" +
            "                    <siri:MaximumStopVisits>1000</siri:MaximumStopVisits>\n" +
            "                </siri:StopMonitoringRequest>\n" +
            "            </Request>\n" +
            "        </siriWS:GetStopMonitoringService>\n" +
            "    </SOAP-ENV:Body>\n" +
            "</SOAP-ENV:Envelope>\n" ;

    @Override
    public String retrieveOneStop(String stopCode, String previewInterval, int maxStopVisits) {
        final String oneStopRequestXml = "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"\n" +
                "                   xmlns:SOAP-ENC=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:acsb=\"http://www.ifopt.org.uk/acsb\"\n" +
                "                   xmlns:datex2=\"http://datex2.eu/schema/1_0/1_0\" xmlns:ifopt=\"http://www.ifopt.org.uk/ifopt\"\n" +
                "                   xmlns:siri=\"http://www.siri.org.uk/siri\" xmlns:siriWS=\"http://new.webservice.namespace\"\n" +
                "                   xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n" +
                "                   xsi:schemaLocation=\"http://192.241.154.128/static/siri/siri.xsd\">\n" +
                "    <SOAP-ENV:Header/>\n" +
                "    <SOAP-ENV:Body>\n" +
                "        <siriWS:GetStopMonitoringService>\n" +
                "            <Request xsi:type=\"siri:ServiceRequestStructure\">\n" +
                "                <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
                "                <siri:RequestorRef xsi:type=\"siri:ParticipantRefStructure\">ML909091</siri:RequestorRef>\n" +
                "                <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\">0100700:1351669188:4684</siri:MessageIdentifier>\n" +
                "                <siri:StopMonitoringRequest version=\"IL2.7\" xsi:type=\"siri:StopMonitoringRequestStructure\">\n" +
                "                    <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
                "                    <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\"></siri:MessageIdentifier>\n" +
                "                    <siri:PreviewInterval>__PREVIEW_INTERVAL__</siri:PreviewInterval>\n" +
                "                    <siri:MonitoringRef xsi:type=\"siri:MonitoringRefStructure\">__STOP_CODE__</siri:MonitoringRef>\n" +
                "                    <siri:MaximumStopVisits>__MAX_STOP_VISITS__</siri:MaximumStopVisits>\n" +
                "                </siri:StopMonitoringRequest>\n" +
                "            </Request>\n" +
                "        </siriWS:GetStopMonitoringService>\n" +
                "    </SOAP-ENV:Body>\n" +
                "</SOAP-ENV:Envelope>\n" ;
        RestTemplate restTemplate = new RestTemplate();
        String url = SIRI_SERVICES_URL;
        String requestXmlString = oneStopRequestXml.replaceAll("__TIMESTAMP__", generateTimestamp())
                .replaceAll("__MAX_STOP_VISITS__", Integer.toString(maxStopVisits))
                .replaceAll("__PREVIEW_INTERVAL__", previewInterval)
                .replaceAll("__STOP_CODE__", stopCode);

        HttpEntity<String> entity = new HttpEntity<String>(requestXmlString, createHeaders());
        logger.trace(requestXmlString);
        ResponseEntity<String> r = restTemplate.postForEntity(url, entity, String.class);
        logger.info("status={}", r.getStatusCode());
        logger.trace("statusCodeValue={}", r.getStatusCodeValue());
        return r.getBody();
    }

    private String generateStopMonitoringRequestTemplate(int minutesFromNow) {
        String template =
                "                <siri:StopMonitoringRequest version=\"IL2.7\" xsi:type=\"siri:StopMonitoringRequestStructure\">\n" +
                        "                    <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
                        "                    <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\"></siri:MessageIdentifier>\n" +
                        "                    <siri:PreviewInterval>__PREVIEW_INTERVAL__</siri:PreviewInterval>\n" +
                        "                    <siri:StartTime>__START__</siri:StartTime>\n" +
                        "                    <siri:LineRef>__LINE_REF__</siri:LineRef>\n" +
                        "                    <siri:MonitoringRef xsi:type=\"siri:MonitoringRefStructure\">__STOP_CODE__</siri:MonitoringRef>\n" +
                        "                    <siri:MaximumStopVisits>__MAX_STOP_VISITS__</siri:MaximumStopVisits>\n" +
                        "                </siri:StopMonitoringRequest>\n" ;

        return template.replace("__START__", generateTimestamp( LocalDateTime.now().plusMinutes(minutesFromNow) ));
    }

    private String generateStopMonitoringServiceRequestTemplate(int numberOfIntervals) {
        String template = "" +
                "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"\n" +
                "                   xmlns:SOAP-ENC=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:acsb=\"http://www.ifopt.org.uk/acsb\"\n" +
                "                   xmlns:datex2=\"http://datex2.eu/schema/1_0/1_0\" xmlns:ifopt=\"http://www.ifopt.org.uk/ifopt\"\n" +
                "                   xmlns:siri=\"http://www.siri.org.uk/siri\" xmlns:siriWS=\"http://new.webservice.namespace\"\n" +
                "                   xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n" +
                "                   xsi:schemaLocation=\"http://192.241.154.128/static/siri/siri.xsd\">\n" +
                "    <SOAP-ENV:Header/>\n" +
                "    <SOAP-ENV:Body>\n" +
                "        <siriWS:GetStopMonitoringService>\n" +
                "            <Request xsi:type=\"siri:ServiceRequestStructure\">\n" +
                "                <siri:RequestTimestamp>__TIMESTAMP__</siri:RequestTimestamp>\n" +
                "                <siri:RequestorRef xsi:type=\"siri:ParticipantRefStructure\">ML909091</siri:RequestorRef>\n" +
                "                <siri:MessageIdentifier xsi:type=\"siri:MessageQualifierStructure\">0100700:1351669188:4684</siri:MessageIdentifier>\n" +
                "__REQUESTS__" +
                "            </Request>\n" +
                "        </siriWS:GetStopMonitoringService>\n" +
                "    </SOAP-ENV:Body>\n" +
                "</SOAP-ENV:Envelope>\n" ;
        String s = "" ;
        logger.trace("generating {} intervals", numberOfIntervals);
        for (int i = 0 ; i < numberOfIntervals ; i = i + 1) {   // intervals of 5 minutes
            s = s + generateStopMonitoringRequestTemplate(i*durationOfIntervalInMinutes);
        }
        return template.replace("__REQUESTS__", s);

    }
    // lineRef 19740 is 947
    // localhost:9000/data/oneStop/20594/7023/PT4H - 480 Jer-TA
//line 420 from BS to Jer - route_id 15531 (15532?), last stop: stopId=11734, stopCode=6109
    // localhost:8080/data/soap/oneStop/6109/15531/PT2D
    private String buildServiceRequest(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        final String oneStopServiceRequestXml = generateStopMonitoringServiceRequestTemplate(numberOfIntervals);    // 12 intervals of 5 minutes
        String requestXmlString = oneStopServiceRequestXml.replaceAll("__TIMESTAMP__", generateTimestamp())
                .replaceAll("__MAX_STOP_VISITS__", Integer.toString(maxStopVisits))
                .replaceAll("__PREVIEW_INTERVAL__", previewInterval)
                .replaceAll("__LINE_REF__", lineRef)
                .replaceAll("__STOP_CODE__", stopCode);
        return  requestXmlString;
    }


    @Override
    public String retrieveFromSiri(String request) {
        logger.info("timestamp={}", generateTimestamp());
        RestTemplate restTemplate = new RestTemplate();
        String url = SIRI_SERVICES_URL;
        String requestXmlString = request.replaceAll("__TIMESTAMP__", generateTimestamp());
        logger.trace(requestXmlString);
        HttpEntity<String> entity = new HttpEntity<String>(requestXmlString, createHeaders());
        //ResponseEntity<String> r = restTemplate.exchange(url, HttpMethod.POST, entity, String.class);
        ResponseEntity<String> r = restTemplate.postForEntity(url, entity, String.class);
        logger.info("status={}", r.getStatusCode());
        logger.trace("statusCodeValue={}", r.getStatusCodeValue());
        return r.getBody();
    }

    private String removeSoapEnvelope(String content) {
        // remove soap envelope (ugly)
        final String prefix = "<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S=\"http://schemas.xmlsoap.org/soap/envelope/\"><S:Body>";
        final String suffix = "</S:Body></S:Envelope>";
        if (content.startsWith(prefix)) {
            content = content.substring(prefix.length());
        }
        if (content.endsWith(suffix)) {
            content = content.substring(0,content.length()-suffix.length());
        }
        return content;
    }

    private GetStopMonitoringServiceResponse unmarshalXml(String xml) {
        try {
            Unmarshaller jaxbUnmarshaller = localUnmarshaller.get();
            if (jaxbUnmarshaller == null) {
                JAXBContext jaxbContext = JAXBContext.newInstance(GetStopMonitoringServiceResponse.class);
                jaxbUnmarshaller = jaxbContext.createUnmarshaller();
                localUnmarshaller.set(jaxbUnmarshaller);
            }
            StreamSource streamSource = new StreamSource(new StringReader(xml));
            JAXBElement<GetStopMonitoringServiceResponse> je = jaxbUnmarshaller.unmarshal(streamSource, GetStopMonitoringServiceResponse.class);

            GetStopMonitoringServiceResponse response = (GetStopMonitoringServiceResponse) je.getValue();
            response.setXmlContent(xml);
            return response;
        }
        catch (JAXBException e) {
            e.printStackTrace();
            return null;
        }
    }

}
