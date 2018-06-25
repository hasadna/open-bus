package org.hasadna.bus.service;

import java.util.List;

public class SchedulingData {
    public List<Command> d ;
    public int dummy = 0;

    public SchedulingData() {
    }

    public SchedulingData(List<Command> data, int dummy) {
        this.d = data;
        this.dummy = dummy;
    }

    public SchedulingData(List<Command> data) {
        this.d = data;
    }
}
