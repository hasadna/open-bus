package org.hasadna.bus.service;

import io.micrometer.datadog.DatadogConfig;
import org.springframework.stereotype.Component;

@Component
public class NullDatadogConfig implements DatadogConfig {
    @Override
    public String prefix() {
        return null;
    }

    @Override
    public String get(String s) {
        return null;
    }

    @Override
    public String apiKey() {
        return "";
    }

    @Override
    public String applicationKey() {
        return null;
    }

    @Override
    public String hostTag() {
        return null;
    }

    @Override
    public String uri() {
        return "http://www.example.com";
    }

    @Override
    public boolean descriptions() {
        return false;
    }
}
