package org.hasadna.bus.service;

import io.micrometer.core.instrument.Clock;
import io.micrometer.datadog.DatadogConfig;
import io.micrometer.datadog.DatadogMeterRegistry;
import org.springframework.stereotype.Component;

@Component
public class NullDatadogMeterRegistry extends DatadogMeterRegistry {
    public NullDatadogMeterRegistry(DatadogConfig config, Clock clock) {
        super(config, clock);
    }
}
