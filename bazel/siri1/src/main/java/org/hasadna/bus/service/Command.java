package org.hasadna.bus.service;

public class Command {
    public String stopCode;
    public String previewInterval;
    public String lineRef;
    public int maxStopVisits;

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits) {
        this.stopCode = stopCode;
        this.previewInterval = previewInterval;
        this.lineRef = lineRef;
        this.maxStopVisits = maxStopVisits;
    }


    Command myClone() {
        return new Command(this.stopCode, this.previewInterval, this.lineRef, this.maxStopVisits);
    }

    @Override
    public String toString() {
        return "Command{" +
                "stopCode='" + stopCode + '\'' +
                ", previewInterval='" + previewInterval + '\'' +
                ", lineRef='" + lineRef + '\'' +
                ", maxStopVisits=" + maxStopVisits +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Command command = (Command) o;

        if (maxStopVisits != command.maxStopVisits) return false;
        if (!stopCode.equals(command.stopCode)) return false;
        if (!previewInterval.equals(command.previewInterval)) return false;
        return lineRef.equals(command.lineRef);
    }

    @Override
    public int hashCode() {
        int result = stopCode.hashCode();
        result = 31 * result + previewInterval.hashCode();
        result = 31 * result + lineRef.hashCode();
        result = 31 * result + maxStopVisits;
        return result;
    }

}