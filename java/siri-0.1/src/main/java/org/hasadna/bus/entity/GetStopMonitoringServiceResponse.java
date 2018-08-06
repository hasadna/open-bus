package org.hasadna.bus.entity;

import javax.xml.bind.annotation.*;

@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "GetStopMonitoringServiceResponseStructure", namespace = "http://new.webservice.namespace")
@XmlRootElement
public class GetStopMonitoringServiceResponse {

    @XmlElement(name = "Answer")
    StopMonitoringAnswer answer;

    @XmlTransient
    private String xmlContent ;

    public StopMonitoringAnswer getAnswer() {
        return answer;
    }

    public void setAnswer(StopMonitoringAnswer answer) {
        this.answer = answer;
    }

    public String getXmlContent() {
        return xmlContent;
    }

    public void setXmlContent(String xmlContent) {
        this.xmlContent = xmlContent;
    }
}
