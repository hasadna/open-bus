package org.hasadna.bus.entity.gtfs;

public class Trip {
    public String tripId;
    public String serviceId;
    public String routeId;
    public String directionId;
    public String shapeId;

    public Trip(String tripId, String serviceId, String routeId, String directionId, String shapeId) {
        this.tripId = tripId;
        this.serviceId = serviceId;
        this.routeId = routeId;
        this.directionId = directionId;
        this.shapeId = shapeId;
    }

    @Override
    public String toString() {
        return "Trip{" +
                "tripId='" + tripId + '\'' +
                ", serviceId='" + serviceId + '\'' +
                ", routeId='" + routeId + '\'' +
                ", directionId='" + directionId + '\'' +
                ", shapeId='" + shapeId + '\'' +
                '}';
    }
}
