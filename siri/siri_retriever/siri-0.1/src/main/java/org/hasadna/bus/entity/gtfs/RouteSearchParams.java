package org.hasadna.bus.entity.gtfs;

public class RouteSearchParams {

    public String publishedName;
    public String cityName;

    public RouteSearchParams() {
        this.publishedName = "";
        this.cityName = "";
    }

    public RouteSearchParams(String publishedName, String cityName) {
        this.publishedName = publishedName;
        this.cityName = cityName;
    }
}
