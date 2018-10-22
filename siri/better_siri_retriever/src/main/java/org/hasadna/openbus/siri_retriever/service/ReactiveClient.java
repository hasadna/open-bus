package org.hasadna.openbus.siri_retriever.service;

import org.hasadna.openbus.siri_retriever.entity.Command;
import org.hasadna.openbus.siri_retriever.entity.GetStopMonitoringServiceResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

import static org.hasadna.openbus.siri_retriever.entity.Command.DEFAULT_CLOCK;

@Service
public class ReactiveClient {

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());
    final String SIRI_SERVICES_URL = "http://siri.motrealtime.co.il:8081/Siri/SiriServices";

    private static final int port = 8081;
    private WebClient webClient;

//    @Autowired
//    private SiriConsumeService siriConsumeService;



    public void doRequest(String requestXml) {
        display(requestXml);
        this.webClient = WebClient.create("http://siri.motrealtime.co.il:" + this.port);
//        Mono<ClientResponse> clientResponse;
//        clientResponse =
//                webClient.post().uri("/Siri/SiriServices").
//                accept(MediaType.APPLICATION_XML)
//                    .body(Mono.just(requestXml), String.class).exchange();

        Mono<ResponseEntity<String>> result = webClient.post().uri("/Siri/SiriServices")
                .accept(MediaType.APPLICATION_XML)
                .contentType(MediaType.TEXT_XML)
                .body(Mono.just(requestXml), String.class)
                .exchange()
                .flatMap(response -> response.toEntity(String.class))
                .flatMap(entity -> Mono.just(entity))
                ;

        result.subscribe(
                resp -> {
                    logger.info("received response, status={}", resp.getStatusCode());
                    logger.info("response as string: {}", resp.toString());
                }
        );
    }

    private Mono<ClientResponse> display(Mono<ClientResponse> response) {
        return Mono.empty();
    }

    private void display(String requestXml) {
        logger.trace(requestXml);
    }

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
        String requestXmlString = oneStopRequestXml.replaceAll("__TIMESTAMP__", generateTimestamp())
                .replaceAll("__MAX_STOP_VISITS__", Integer.toString(maxStopVisits))
                .replaceAll("__PREVIEW_INTERVAL__", previewInterval)
                .replaceAll("__STOP_CODE__", stopCode);
        return  requestXmlString;
    }

    private String generateTimestamp() {
        return LocalDateTime.now(DEFAULT_CLOCK).format(DateTimeFormatter.ISO_DATE_TIME);
    }


    @Scheduled(fixedRate=60000, initialDelay = 5000)    // every 1 minutes.
    public void exec() {
        logger.info("starting exec ...");

        Command c = new Command(
                //this.stopCode = stopCode;
                "42658",
//        this.previewInterval = previewInterval;
                "PT60M",
//        this.lineRef = lineRef;
                "123",
//        this.maxStopVisits = maxStopVisits;
                7,
//        this.nextExecution = nextExecution;
                null,
//        this.executeEvery = executeEvery;
                2,
//        this.description = description;
                "abc",
//        this.weeklyDepartureTimes = weeklyDepartureTimes;
                null,
//        this.lastArrivalTimes = lastArrivalTimes;
                null
        );

        String requestXml = retrieveOneStop(c.stopCode, c.previewInterval, c.maxStopVisits);
        logger.trace("retrieving {} ...", c.lineRef);
        doRequest(requestXml);      // temporarily log the response
        //GetStopMonitoringServiceResponse result = siriConsumeService.retrieveSiri(c);   // this part is synchronous
        logger.debug("retrieving {} ... done", c.lineRef);
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









    public void doRequest1() {
        this.webClient = WebClient.create("http://siri.motrealtime.co.il:" + this.port);

//        Mono<GetStopMonitoringServiceResponse> siriResponse1 = this.webClient.get().uri("/customer/accounts/234543647565")
//                    .accept(MediaType.APPLICATION_JSON).exchange().then(response -> response.bodyToMono(GetStopMonitoringServiceResponse.class))
//                    ; //.block();
//        siriResponse1.subscribe(resp -> logger.info(resp.getXmlContent()));

        Mono<GetStopMonitoringServiceResponse> siriResponse1a = this.webClient.get().uri("/Siri/SiriServices")
                .accept(MediaType.APPLICATION_JSON).exchange().flatMap(response -> response.bodyToMono(GetStopMonitoringServiceResponse.class))
                ; //.doOnNext(stopMonitoringResponse -> stopMonitoringResponse.getXmlContent());
        siriResponse1a.subscribe(resp -> logger.info(resp.getXmlContent()));
        //logger.info("Customer: " + siriResponse1.);


        //GetStopMonitoringServiceResponse siriResponse2 = new GetStopMonitoringServiceResponse(null, "Adam", "Kowalski", "123456787654");
        //Flux<GetStopMonitoringServiceResponse> siriResponse2 = webClient.post().uri("/customer").accept(MediaType.APPLICATION_JSON)
        //            .exchange(BodyInserters.fromObject(customer)).then(response -> response.bodyToMono(GetStopMonitoringServiceResponse.class))
        //            ;

        //Mono<GetStopMonitoringServiceResponse> siriResponse2;
        Mono<ClientResponse> clientResponse;
        clientResponse = webClient.post().uri("/Siri/SiriServices").
                accept(MediaType.APPLICATION_JSON).body(Mono.just(sampleRequestXml), String.class).exchange();

        //BodyInserters.fromObject(sampleRequestXml)).flatMap(response -> response.bodyToMono(GetStopMonitoringServiceResponse.class));
        clientResponse.subscribe(
                resp -> logger.info("received response, status={}", resp.statusCode())
        );
        //logger.info("Customer: " + customer);

    }


}
