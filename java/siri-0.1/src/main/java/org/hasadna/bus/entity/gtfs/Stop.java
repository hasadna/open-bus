package org.hasadna.bus.entity.gtfs;

public class Stop {

    public String stopId;
    public String stopCode;
    public String stopName;
    public String stopDesc;
    public String stopLat;
    public String stopLong;

    public Stop(String stopId, String stopCode, String stopName, String stopDesc, String stopLat, String stopLong) {
        this.stopId = stopId;
        this.stopCode = stopCode;
        this.stopName = stopName;
        this.stopDesc = stopDesc;
        this.stopLat = stopLat;
        this.stopLong = stopLong;
    }

    @Override
    public String toString() {
        return "Stop{" +
                "stopId='" + stopId + '\'' +
                ", stopCode='" + stopCode + '\'' +
                ", stopName='" + stopName + '\'' +
                ", stopDesc='" + stopDesc + '\'' +
                ", stopLat='" + stopLat + '\'' +
                ", stopLong='" + stopLong + '\'' +
                '}';
    }
}
