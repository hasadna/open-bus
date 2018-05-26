package il.org.hasadna.siri_client.gtfs;

import java.util.Arrays;
import java.util.Iterator;

/**
 * @author Aviv Sela
 *
 */
public final class BaseStopTime implements StopTime {

	private final String tripId;
	private final String arrivalTime;
	private final String departureTime;
	private final int stopId;
	private final int stopSequence;
	private final int pickupType;
	private final int dropOffType;
	private final int shapeDistTraveled;

	private static int strToInt(String str) {
		return str.isEmpty() ? 0 : Integer.valueOf(str);
	}

	/**
	 * Parse a standard CSV line into StopTime object
	 * 
	 * @param csvRow
	 * @return StopTime object
	 */
	public static BaseStopTime parse(String csvRow) {

		Iterator<String> iter = Arrays.asList(csvRow.split(",", -1)).iterator();
		String tripId = iter.next();
		String arrivalTime = iter.next();
		String departureTime = iter.next();
		int stopId = strToInt(iter.next());
		int stopSequence = strToInt(iter.next());
		int pickupType = strToInt(iter.next());
		int dropOffType = strToInt(iter.next());
		int shapeDistTraveled = strToInt(iter.next());

		return new BaseStopTime(tripId, arrivalTime, departureTime, stopId, stopSequence, pickupType, dropOffType,
				shapeDistTraveled);
	}

	BaseStopTime(String tripId, String arrivalTime, String departureTime, int stopId, int stopSequence, int pickupType,
			int dropOffType, int shapeDistTraveled) {
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
	public String getTripId() {
		return tripId;
	}

	@Override
	public String getArrivalTime() {
		return arrivalTime;
	}

	@Override
	public String getDepartureTime() {
		return departureTime;
	}

	@Override
	public int getStopId() {
		return stopId;
	}

	@Override
	public int getStopSequence() {
		return stopSequence;
	}

	@Override
	public int getPickupType() {
		return pickupType;
	}

	@Override
	public int getDropOffType() {
		return dropOffType;
	}

	@Override
	public int getShapeDistTraveled() {
		return shapeDistTraveled;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((arrivalTime == null) ? 0 : arrivalTime.hashCode());
		result = prime * result + ((departureTime == null) ? 0 : departureTime.hashCode());
		result = prime * result + dropOffType;
		result = prime * result + pickupType;
		result = prime * result + shapeDistTraveled;
		result = prime * result + stopId;
		result = prime * result + stopSequence;
		result = prime * result + ((tripId == null) ? 0 : tripId.hashCode());
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
		BaseStopTime other = (BaseStopTime) obj;
		if (arrivalTime == null) {
			if (other.arrivalTime != null)
				return false;
		} else if (!arrivalTime.equals(other.arrivalTime))
			return false;
		if (departureTime == null) {
			if (other.departureTime != null)
				return false;
		} else if (!departureTime.equals(other.departureTime))
			return false;
		if (dropOffType != other.dropOffType)
			return false;
		if (pickupType != other.pickupType)
			return false;
		if (shapeDistTraveled != other.shapeDistTraveled)
			return false;
		if (stopId != other.stopId)
			return false;
		if (stopSequence != other.stopSequence)
			return false;
		if (tripId == null) {
			if (other.tripId != null)
				return false;
		} else if (!tripId.equals(other.tripId))
			return false;
		return true;
	}
}
