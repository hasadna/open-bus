package org.hasadna.bus.service;

import org.springframework.stereotype.Component;

@Component
public class NullClock implements io.micrometer.core.instrument.Clock {
    @Override
    public long wallTime() {
        return 0;
    }

    @Override
    public long monotonicTime() {
        return 0;
    }
}
