package org.hasadna.bus.entity.gtfs;

public class StopTimes {
    public String stopId;
    public int stopSequence;
    public String tripId;
    public String arrivalTime;
    public String departureTime;
    public String pickupType;
    public String dropOffType;
    public String shapeDistTraveled;

    public StopTimes(String tripId, String arrivalTime, String departureTime, String stopId, int stopSequence, String pickupType, String dropOffType, String shapeDistTraveled) {
        this.tripId = tripId;
        this.arrivalTime = arrivalTime;
        this.departureTime = departureTime;
        this.stopId = stopId;
        this.stopSequence = stopSequence;
        this.pickupType = pickupType;
        this.dropOffType = dropOffType;
        this.shapeDistTraveled = shapeDistTraveled;
    }

    @Override
    public String toString() {
        return "StopTimes{" +
                "stopId='" + stopId + '\'' +
                ", stopSequence=" + stopSequence +
                ", tripId='" + tripId + '\'' +
                ", arrivalTime='" + arrivalTime + '\'' +
                ", departureTime='" + departureTime + '\'' +
                ", pickupType='" + pickupType + '\'' +
                ", dropOffType='" + dropOffType + '\'' +
                ", shapeDistTraveled='" + shapeDistTraveled + '\'' +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        StopTimes stopTimes = (StopTimes) o;

        if (stopSequence != stopTimes.stopSequence) return false;
        if (tripId != null ? !tripId.equals(stopTimes.tripId) : stopTimes.tripId != null) return false;
        if (arrivalTime != null ? !arrivalTime.equals(stopTimes.arrivalTime) : stopTimes.arrivalTime != null)
            return false;
        if (departureTime != null ? !departureTime.equals(stopTimes.departureTime) : stopTimes.departureTime != null)
            return false;
        if (stopId != null ? !stopId.equals(stopTimes.stopId) : stopTimes.stopId != null) return false;
        if (pickupType != null ? !pickupType.equals(stopTimes.pickupType) : stopTimes.pickupType != null) return false;
        if (dropOffType != null ? !dropOffType.equals(stopTimes.dropOffType) : stopTimes.dropOffType != null)
            return false;
        return shapeDistTraveled != null ? shapeDistTraveled.equals(stopTimes.shapeDistTraveled) : stopTimes.shapeDistTraveled == null;
    }

    @Override
    public int hashCode() {
        int result = tripId != null ? tripId.hashCode() : 0;
        result = 31 * result + (arrivalTime != null ? arrivalTime.hashCode() : 0);
        result = 31 * result + (departureTime != null ? departureTime.hashCode() : 0);
        result = 31 * result + (stopId != null ? stopId.hashCode() : 0);
        result = 31 * result + stopSequence;
        result = 31 * result + (pickupType != null ? pickupType.hashCode() : 0);
        result = 31 * result + (dropOffType != null ? dropOffType.hashCode() : 0);
        result = 31 * result + (shapeDistTraveled != null ? shapeDistTraveled.hashCode() : 0);
        return result;
    }
}
