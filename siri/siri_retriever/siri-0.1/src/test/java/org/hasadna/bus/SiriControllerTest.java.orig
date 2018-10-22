package org.hasadna.bus;

import org.assertj.core.api.Assertions;
import org.hasadna.bus.controller.SiriController;
import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;
import uk.org.siri.siri.MonitoredStopVisitStructure;
import uk.org.siri.siri.StopMonitoringDeliveryStructure;

import java.math.BigDecimal;

@RunWith(SpringRunner.class)
@SpringBootTest
public class SiriControllerTest {

    @Autowired
    SiriController siriController ;

    @Test
    public void test1() {
        GetStopMonitoringServiceResponse response =
            siriController.retrieveSiriDataOneStopAndLineRefAndPreviewIntervalSoap("10331",
                                                                                    "7023",
                                                                                "PT24H", 7);
        Assertions.assertThat(response.getAnswer().isStatus()).isNotNull().isTrue();
        Assertions.assertThat(response.getAnswer().getStopMonitoringDelivery().size()).isEqualTo(3);
        MonitoredStopVisitStructure msvs = response.getAnswer().getStopMonitoringDelivery().get(0).getMonitoredStopVisit().get(0);
        Assertions.assertThat(msvs.getMonitoringRef().getValue()).isNotNull().isEqualTo("20594");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getLineRef().getValue()).isEqualTo("7023");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getDirectionRef().getValue()).isEqualTo("3");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getPublishedLineName().getValue()).isEqualTo("480");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getOriginAimedDepartureTime()).isBefore("2018-06-01").isAfter("2018-05-30");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getMonitoredCall().getAimedArrivalTime()).isNull();
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getMonitoredCall().getExpectedArrivalTime()).isAfter(msvs.getMonitoredVehicleJourney().getOriginAimedDepartureTime());
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getVehicleLocation()).isNotNull();
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getVehicleLocation().getLatitude()).isBetween(BigDecimal.valueOf(30), BigDecimal.valueOf(36));
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getVehicleLocation().getLongitude()).isBetween(BigDecimal.valueOf(30), BigDecimal.valueOf(36));
    }

    @Test
    public void test2() {
        GetStopMonitoringServiceResponse response =
                siriController.retrieveSiriDataOneStopAndLineRefAndPreviewIntervalSoap("20594",
                                                                                        "7453",
                                                                                        "PT2H",7);
        // when no real-time data, only planned, the answer.status is Null
        Assertions.assertThat(response.getAnswer().getStatus()).isNull();
        // However, we have answer.responseTimestamp
        Assertions.assertThat(response.getAnswer().getResponseTimestamp()).isNotNull().isBefore("2018-06-02");
        // and we have StopMonitoringDelivery.status = true
        Assertions.assertThat(response.getAnswer().getStopMonitoringDelivery().size()).isEqualTo(3);
        StopMonitoringDeliveryStructure smds = response.getAnswer().getStopMonitoringDelivery().get(0);
        Assertions.assertThat(smds.getResponseTimestamp()).isNotNull();
        Assertions.assertThat(smds.isStatus()).isTrue();
        Assertions.assertThat(smds.getMonitoredStopVisit().size()).isEqualTo(2);
        MonitoredStopVisitStructure msvs = smds.getMonitoredStopVisit().get(0);
        Assertions.assertThat(msvs.getMonitoringRef().getValue()).isNotNull().isEqualTo("10331");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getLineRef().getValue()).isEqualTo("7453");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getDirectionRef().getValue()).isEqualTo("2");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getPublishedLineName().getValue()).isEqualTo("394");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getOriginAimedDepartureTime()).isBefore("2018-06-03").isAfter("2018-05-31");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getMonitoredCall().getAimedArrivalTime()).isBefore("2018-06-03");
        Assertions.assertThat(msvs.getMonitoredVehicleJourney().getMonitoredCall().getExpectedArrivalTime()).isEqualTo(msvs.getMonitoredVehicleJourney().getMonitoredCall().getAimedArrivalTime());
    }
}
