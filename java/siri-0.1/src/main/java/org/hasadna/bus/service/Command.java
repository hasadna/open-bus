package org.hasadna.bus.service;

import com.fasterxml.jackson.annotation.JsonIgnore;

import java.time.LocalDateTime;

public class Command {
    public String description = "";
    public String stopCode;
    public String previewInterval;
    public String lineRef;
    public int maxStopVisits;
    @JsonIgnore
    public LocalDateTime nextExecution;
    public int executeEvery;

    public Command() {
    }

    public Command(String stopCode) {
        this.stopCode = stopCode;
    }

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits, int executeEvery, String description) {
        this(stopCode, previewInterval, lineRef, maxStopVisits, LocalDateTime.now(), executeEvery, description);
    }

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits, LocalDateTime nextExecution, int executeEvery) {
        this(stopCode, previewInterval, lineRef, maxStopVisits, nextExecution, executeEvery, "");
    }

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits, LocalDateTime nextExecution, int executeEvery, String description) {
        this.stopCode = stopCode;
        this.previewInterval = previewInterval;
        this.lineRef = lineRef;
        this.maxStopVisits = maxStopVisits;
        this.nextExecution = nextExecution;
        this.executeEvery = executeEvery;
        this.description = description;
    }

    Command myClone() {
        return new Command(this.stopCode, this.previewInterval, this.lineRef, this.maxStopVisits, this.nextExecution, this.executeEvery, this.description);
    }

    @Override
    public String toString() {
        return "Command{" +
                "description='" + description + '\'' +
                ", stopCode='" + stopCode + '\'' +
                ", previewInterval='" + previewInterval + '\'' +
                ", lineRef='" + lineRef + '\'' +
                ", maxStopVisits=" + maxStopVisits +
                ", nextExecution=" + nextExecution +
                ", executeEvery=" + executeEvery +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Command command = (Command) o;

        if (maxStopVisits != command.maxStopVisits) return false;
        if (executeEvery != command.executeEvery) return false;
        if (stopCode != null ? !stopCode.equals(command.stopCode) : command.stopCode != null) return false;
        if (previewInterval != null ? !previewInterval.equals(command.previewInterval) : command.previewInterval != null)
            return false;
        if (lineRef != null ? !lineRef.equals(command.lineRef) : command.lineRef != null) return false;
        return nextExecution != null ? nextExecution.equals(command.nextExecution) : command.nextExecution == null;
    }

    @Override
    public int hashCode() {
        int result = stopCode != null ? stopCode.hashCode() : 0;
        result = 31 * result + (previewInterval != null ? previewInterval.hashCode() : 0);
        result = 31 * result + (lineRef != null ? lineRef.hashCode() : 0);
        result = 31 * result + maxStopVisits;
        result = 31 * result + (nextExecution != null ? nextExecution.hashCode() : 0);
        result = 31 * result + executeEvery;
        return result;
    }
}