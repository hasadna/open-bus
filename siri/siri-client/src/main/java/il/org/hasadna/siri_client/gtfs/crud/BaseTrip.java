package il.org.hasadna.siri_client.gtfs.crud;

import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

/**
 * @author Aviv Sela
 *
 */
public final class BaseTrip implements Trip {
	final private String routeId;
	final private ServiceId serviceId;
	final private String tripId;
	final private String tripHeadsign;
	final private int directionId;
	final private int shapeId;

	/**
	 * Parse a standard CSV line into Trip object
	 * 
	 * @param csvRow
	 * @return Trip object
	 */
	public static BaseTrip parse(String csvRow) {

		List<String> items = Arrays.asList(csvRow.split(",", -1));

		Iterator<String> iter = items.iterator();
		String routeId = iter.next();
		ServiceId serviceId = new ServiceId(iter.next());
		String tripId = iter.next();
		String tripHeadsign = iter.next();
		int directionId = Integer.valueOf(iter.next());

		String shapeIdStr = iter.next();
		int shapeId = shapeIdStr.isEmpty() ? 0 : Integer.valueOf(shapeIdStr);

		return new BaseTrip(routeId, serviceId, tripId, tripHeadsign, directionId, shapeId);
	}

	public BaseTrip(String routeId, ServiceId serviceId, String tripId, String tripHeadsign, int directionId,
			int shapeId) {
		super();
		this.routeId = routeId;
		this.serviceId = serviceId;
		this.tripId = tripId;
		this.tripHeadsign = tripHeadsign;
		this.directionId = directionId;
		this.shapeId = shapeId;
	}

	@Override
	public String getRouteId() {
		return routeId;
	}

	@Override
	public ServiceId getServiceId() {
		return serviceId;
	}

	@Override
	public String getTripId() {
		return tripId;
	}

	@Override
	public String getTripHeadsign() {
		return tripHeadsign;
	}

	@Override
	public int getDirectionId() {
		return directionId;
	}

	@Override
	public int getShapeId() {
		return shapeId;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + directionId;
		result = prime * result + ((routeId == null) ? 0 : routeId.hashCode());
		result = prime * result + ((serviceId == null) ? 0 : serviceId.hashCode());
		result = prime * result + shapeId;
		result = prime * result + ((tripHeadsign == null) ? 0 : tripHeadsign.hashCode());
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
		BaseTrip other = (BaseTrip) obj;
		if (directionId != other.directionId)
			return false;
		if (routeId == null) {
			if (other.routeId != null)
				return false;
		} else if (!routeId.equals(other.routeId))
			return false;
		if (serviceId == null) {
			if (other.serviceId != null)
				return false;
		} else if (!serviceId.equals(other.serviceId))
			return false;
		if (shapeId != other.shapeId)
			return false;
		if (tripHeadsign == null) {
			if (other.tripHeadsign != null)
				return false;
		} else if (!tripHeadsign.equals(other.tripHeadsign))
			return false;
		if (tripId == null) {
			if (other.tripId != null)
				return false;
		} else if (!tripId.equals(other.tripId))
			return false;
		return true;
	}

	@Override
	public String toString() {
		return "BaseTrip [" + (routeId != null ? "routeId=" + routeId + ", " : "")
				+ (serviceId != null ? "serviceId=" + serviceId + ", " : "")
				+ (tripId != null ? "tripId=" + tripId + ", " : "")
				+ (tripHeadsign != null ? "tripHeadsign=" + tripHeadsign + ", " : "") + "directionId=" + directionId
				+ ", shapeId=" + shapeId + "]";
	}
	
	
	

}
