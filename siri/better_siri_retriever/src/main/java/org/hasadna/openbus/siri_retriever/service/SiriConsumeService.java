package org.hasadna.openbus.siri_retriever.service;


import org.hasadna.openbus.siri_retriever.entity.Command;
import org.hasadna.openbus.siri_retriever.entity.GetStopMonitoringServiceResponse;

public interface SiriConsumeService {

    GetStopMonitoringServiceResponse retrieveSiri(String stopCode, String previewInterval, String lineRef, int maxStopVisits);
    GetStopMonitoringServiceResponse retrieveSiri(Command command);



    String retrieveFromSiri(String request);
    String retrieveOneStop(String stopCode, String previewInterval, int maxStopVisits);
    String retrieveSpecificLineAndStop(String stopCode, String previewInterval, String lineRef, int maxStopVisits);
}
