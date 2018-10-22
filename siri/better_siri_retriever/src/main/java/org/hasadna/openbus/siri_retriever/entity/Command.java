package org.hasadna.openbus.siri_retriever.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.time.Clock;
import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

//import static org.hasadna.bus.util.DateTimeUtils.DEFAULT_CLOCK;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Command {
    public String description = "";
    public String makat = "";
    public String stopCode;
    public String lineShortName = "";
    public String previewInterval;
    public String lineRef;
    public int maxStopVisits;
    @JsonIgnore
    public LocalDateTime nextExecution;
    @JsonIgnore
    public boolean isActive = true;
    public int executeEvery;
    public List<LocalTime[]> activeRanges;
    public Map<DayOfWeek, List<String>> weeklyDepartureTimes;
    public Map<DayOfWeek, String> lastArrivalTimes;

    // backward compatibility for previous json schema
    @JsonIgnore
    public List<String> departureTimes;


    public static Clock DEFAULT_CLOCK = Clock.systemDefaultZone();


    public Command() {
    }

    public Command(String stopCode) {
        this.stopCode = stopCode;
    }

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits, int executeEvery, String description) {
        this(stopCode, previewInterval, lineRef, maxStopVisits, LocalDateTime.now(DEFAULT_CLOCK), executeEvery, description, new HashMap<>(), new HashMap<>());
    }

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits, LocalDateTime nextExecution, int executeEvery) {
        this(stopCode, previewInterval, lineRef, maxStopVisits, nextExecution, executeEvery, "", new HashMap<>(), new HashMap<>());
    }

    public Command(String stopCode, String previewInterval, String lineRef, int maxStopVisits, LocalDateTime nextExecution, int executeEvery, String description, Map<DayOfWeek, List<String>> weeklyDepartureTimes, Map<DayOfWeek, String> lastArrivalTimes) {
        this.stopCode = stopCode;
        this.previewInterval = previewInterval;
        this.lineRef = lineRef;
        this.maxStopVisits = maxStopVisits;
        this.nextExecution = nextExecution;
        this.executeEvery = executeEvery;
        this.description = description;
        this.weeklyDepartureTimes = weeklyDepartureTimes;
        this.lastArrivalTimes = lastArrivalTimes;
    }

    Command myClone() {
        return new Command(this.stopCode, this.previewInterval, this.lineRef, this.maxStopVisits, this.nextExecution, this.executeEvery, this.description, this.weeklyDepartureTimes, this.lastArrivalTimes);
    }

    @Override
    public String toString() {
        return "Command{" +
                "description='" + description + '\'' +
                ", makat='" + makat + '\'' +
                ", stopCode='" + stopCode + '\'' +
                ", lineShortName='" + lineShortName + '\'' +
                ", previewInterval='" + previewInterval + '\'' +
                ", lineRef='" + lineRef + '\'' +
                ", maxStopVisits=" + maxStopVisits +
                ", " + (isActive?" ":" NOT ") + "Active" +
                ", nextExecution=" + nextExecution +
                ", executeEvery=" + executeEvery +
                ", weeklyDepartureTimes=" + weeklyDepartureTimes +
                ", lastArrivalTimes=" + lastArrivalTimes +
                '}';
    }


    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Command command = (Command) o;

        if (maxStopVisits != command.maxStopVisits) return false;
        if (isActive != command.isActive) return false;
        if (executeEvery != command.executeEvery) return false;
        if (description != null ? !description.equals(command.description) : command.description != null) return false;
        if (makat != null ? !makat.equals(command.makat) : command.makat != null) return false;
        if (stopCode != null ? !stopCode.equals(command.stopCode) : command.stopCode != null) return false;
        if (lineShortName != null ? !lineShortName.equals(command.lineShortName) : command.lineShortName != null)
            return false;
        if (previewInterval != null ? !previewInterval.equals(command.previewInterval) : command.previewInterval != null)
            return false;
        if (lineRef != null ? !lineRef.equals(command.lineRef) : command.lineRef != null) return false;
        if (nextExecution != null ? !nextExecution.equals(command.nextExecution) : command.nextExecution != null)
            return false;
        if (activeRanges != null ? !activeRanges.equals(command.activeRanges) : command.activeRanges != null)
            return false;
        if (weeklyDepartureTimes != null ? !weeklyDepartureTimes.equals(command.weeklyDepartureTimes) : command.weeklyDepartureTimes != null)
            return false;
        if (lastArrivalTimes != null ? !lastArrivalTimes.equals(command.lastArrivalTimes) : command.lastArrivalTimes != null)
            return false;
        return departureTimes != null ? departureTimes.equals(command.departureTimes) : command.departureTimes == null;
    }

    @Override
    public int hashCode() {
        int result = description != null ? description.hashCode() : 0;
        result = 31 * result + (makat != null ? makat.hashCode() : 0);
        result = 31 * result + (stopCode != null ? stopCode.hashCode() : 0);
        result = 31 * result + (lineShortName != null ? lineShortName.hashCode() : 0);
        result = 31 * result + (previewInterval != null ? previewInterval.hashCode() : 0);
        result = 31 * result + (lineRef != null ? lineRef.hashCode() : 0);
        result = 31 * result + maxStopVisits;
        result = 31 * result + (nextExecution != null ? nextExecution.hashCode() : 0);
        result = 31 * result + (isActive ? 1 : 0);
        result = 31 * result + executeEvery;
        result = 31 * result + (activeRanges != null ? activeRanges.hashCode() : 0);
        result = 31 * result + (weeklyDepartureTimes != null ? weeklyDepartureTimes.hashCode() : 0);
        result = 31 * result + (lastArrivalTimes != null ? lastArrivalTimes.hashCode() : 0);
        result = 31 * result + (departureTimes != null ? departureTimes.hashCode() : 0);
        return result;
    }
}