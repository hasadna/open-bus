package org.hasadna.bus.service;

import org.hasadna.bus.entity.GetStopMonitoringServiceResponse;

import java.util.Optional;

public interface SiriParseService {
    Optional<String> parseShortSummary(GetStopMonitoringServiceResponse sm);
}
