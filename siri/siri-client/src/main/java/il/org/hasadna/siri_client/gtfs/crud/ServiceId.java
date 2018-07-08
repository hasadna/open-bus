package il.org.hasadna.siri_client.gtfs.crud;

/**
 * The calendar service_id contains an ID that uniquely identifies a set of dates
 * when service is available for one or more routes. Each service_id value
 * can appear at most once in a calendar.txt file. This value is data set
 * unique. It is referenced by the trips.txt file.
 */
public final class ServiceId {
	private final String serviceId;

	public ServiceId(String serviceId) {
		this.serviceId = serviceId;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((serviceId == null) ? 0 : serviceId.hashCode());
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
		ServiceId other = (ServiceId) obj;
		if (serviceId == null) {
			if (other.serviceId != null)
				return false;
		} else if (!serviceId.equals(other.serviceId))
			return false;
		return true;
	}

	@Override
	public String toString() {
		return "ServiceId [serviceId=" + serviceId + "]";
	}

}
