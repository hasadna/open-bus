package il.org.hasadna.siri_client.gtfs.analysis;

import java.util.Objects;

import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.Stop;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public final class GtfsRecord {

	final private Trip trip;
	final private Calendar calendar; 
	final private StopTime firstStopTime;
	final private Stop firstStop;
	final private StopTime lastStopTime;
	final private Stop lastStop;
	
	
	GtfsRecord(Trip trip, Calendar calendar, StopTime firstStopTime, Stop firstStop, StopTime lastStopTime,
			Stop lastStop) {
		
		this.trip = Objects.requireNonNull(trip);
		this.calendar = Objects.requireNonNull(calendar);
		this.firstStopTime = Objects.requireNonNull(firstStopTime);
		this.firstStop = Objects.requireNonNull(firstStop);
		this.lastStopTime = Objects.requireNonNull(lastStopTime);
		this.lastStop = Objects.requireNonNull(lastStop);
	}


	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((calendar == null) ? 0 : calendar.hashCode());
		result = prime * result + ((firstStop == null) ? 0 : firstStop.hashCode());
		result = prime * result + ((firstStopTime == null) ? 0 : firstStopTime.hashCode());
		result = prime * result + ((lastStop == null) ? 0 : lastStop.hashCode());
		result = prime * result + ((lastStopTime == null) ? 0 : lastStopTime.hashCode());
		result = prime * result + ((trip == null) ? 0 : trip.hashCode());
		return result;
	}


	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		GtfsRecord other = (GtfsRecord) obj;
		if (calendar == null) {
			if (other.calendar != null)
				return false;
		} else if (!calendar.equals(other.calendar))
			return false;
		if (firstStop == null) {
			if (other.firstStop != null)
				return false;
		} else if (!firstStop.equals(other.firstStop))
			return false;
		if (firstStopTime == null) {
			if (other.firstStopTime != null)
				return false;
		} else if (!firstStopTime.equals(other.firstStopTime))
			return false;
		if (lastStop == null) {
			if (other.lastStop != null)
				return false;
		} else if (!lastStop.equals(other.lastStop))
			return false;
		if (lastStopTime == null) {
			if (other.lastStopTime != null)
				return false;
		} else if (!lastStopTime.equals(other.lastStopTime))
			return false;
		if (trip == null) {
			if (other.trip != null)
				return false;
		} else if (!trip.equals(other.trip))
			return false;
		return true;
	}


	public Trip getTrip() {
		return trip;
	}


	public Calendar getCalendar() {
		return calendar;
	}


	public StopTime getFirstStopTime() {
		return firstStopTime;
	}


	public Stop getFirstStop() {
		return firstStop;
	}


	public StopTime getLastStopTime() {
		return lastStopTime;
	}


	public Stop getLastStop() {
		return lastStop;
	}


	@Override
	public String toString() {
		return "GtfsRecord [trip=" + trip + ", calendar=" + calendar + ", firstStopTime=" + firstStopTime
				+ ", firstStop=" + firstStop + ", lastStopTime=" + lastStopTime + ", lastStop=" + lastStop + "]";
	}
	

	
	
	


}
