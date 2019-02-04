package org.hasadna.bus.entity;

import uk.org.siri.siri.*;

import javax.xml.bind.annotation.*;
import java.util.List;

@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "ProducerResponseEndpointStructure")
public class StopMonitoringAnswer extends AbstractServiceDeliveryStructure {

    @XmlElement(name = "ProducerRef", namespace = "http://www.siri.org.uk/siri")
    protected ParticipantRefStructure producerRef;

    @XmlElement(name = "ResponseMessageIdentifier", namespace = "http://www.siri.org.uk/siri")
    protected MessageQualifierStructure responseMessageIdentifier;

    @XmlElement(name = "RequestMessageRef", namespace = "http://www.siri.org.uk/siri")
    protected MessageRefStructure requestMessageRef;

    @XmlElement(name = "Status", namespace = "http://www.siri.org.uk/siri")
    Boolean status;

    @XmlElement(name="StopMonitoringDelivery", namespace = "http://www.siri.org.uk/siri")
    List<StopMonitoringDeliveryStructure> stopMonitoringDelivery;


    public ParticipantRefStructure getProducerRef() {
        return producerRef;
    }

    public void setProducerRef(ParticipantRefStructure producerRef) {
        this.producerRef = producerRef;
    }

    public MessageQualifierStructure getResponseMessageIdentifier() {
        return responseMessageIdentifier;
    }

    public void setResponseMessageIdentifier(MessageQualifierStructure responseMessageIdentifier) {
        this.responseMessageIdentifier = responseMessageIdentifier;
    }

    public MessageRefStructure getRequestMessageRef() {
        return requestMessageRef;
    }

    public void setRequestMessageRef(MessageRefStructure requestMessageRef) {
        this.requestMessageRef = requestMessageRef;
    }

    public Boolean getStatus() {
        return status;
    }

    public void setStatus(Boolean status) {
        this.status = status;
    }


    public List<StopMonitoringDeliveryStructure> getStopMonitoringDelivery() {
        return stopMonitoringDelivery;
    }

    public void setStopMonitoringDelivery(List<StopMonitoringDeliveryStructure> stopMonitoringDelivery) {
        this.stopMonitoringDelivery = stopMonitoringDelivery;
    }
}
