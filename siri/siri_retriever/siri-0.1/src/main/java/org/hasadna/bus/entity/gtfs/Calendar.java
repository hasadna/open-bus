package org.hasadna.bus.entity.gtfs;

public class Calendar {
    public String serviceId;
    public String startDate;
    public String endDate;
    public boolean sunday;
    public boolean monday;
    public boolean tuesday;
    public boolean wednesday;
    public boolean thursday;
    public boolean friday;
    public boolean saturday;

    public Calendar(String serviceId, String startDate, String endDate, boolean sunday, boolean monday, boolean tuesday, boolean wednesday, boolean thursday, boolean friday, boolean saturday) {
        this.serviceId = serviceId;
        this.startDate = startDate;
        this.endDate = endDate;
        this.sunday = sunday;
        this.monday = monday;
        this.tuesday = tuesday;
        this.wednesday = wednesday;
        this.thursday = thursday;
        this.friday = friday;
        this.saturday = saturday;
    }

    @Override
    public String toString() {
        return "Calendar{" +
                "serviceId='" + serviceId + '\'' +
                ", startDate='" + startDate + '\'' +
                ", endDate='" + endDate + '\'' +
                (sunday? ", Sunday" : "") +
                (monday? ", Monday" : "") +
                (tuesday? ", Tuesday" : "") +
                (wednesday? ", Wednesday" : "") +
                (thursday? ", Thursday" : "") +
                (friday? ", Friday" : "") +
                (saturday? ", Saturday" : "") +
                '}';
    }
}
