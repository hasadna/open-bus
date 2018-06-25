package org.hasadna.bus.entity.gtfs;

public class Route {
    public String routeId;
    public String agencyId;
    public String routeShortName;
    public String routeLongName;
    public String routeDesc;

    public String routeType = "";
    public String routeColor = "";

    public Route(String routeId, String agencyId, String routeShortName, String routeLongName, String routeDesc) {
        this.routeId = routeId;
        this.agencyId = agencyId;
        this.routeShortName = routeShortName;
        this.routeLongName = routeLongName;
        this.routeDesc = routeDesc;
    }

    @Override
    public String toString() {
        return "Route{" +
                "routeId='" + routeId + '\'' +
                ", agencyId='" + agencyId + '\'' +
                ", routeShortName='" + routeShortName + '\'' +
                ", routeLongName='" + routeLongName + '\'' +
                ", routeDesc='" + routeDesc + '\'' +
                '}';
    }
}
