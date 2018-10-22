package org.hasadna.bus.service;

import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;

public interface SiriProcessService {
    void process(GetStopMonitoringServiceResponse stopMonitorResult);
}
