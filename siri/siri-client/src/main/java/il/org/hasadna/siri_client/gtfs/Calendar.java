package il.org.hasadna.siri_client.gtfs;

import java.time.LocalDate;
import java.util.EnumSet;

public interface Calendar {
	public enum Day {
		SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY;
	}

	/**
	 * The service_id contains an ID that uniquely identifies a set of dates when
	 * service is available for one or more routes. Each service_id value can appear
	 * at most once in a calendar.txt file. This value is data set unique. It is
	 * referenced by the trips.txt file.
	 */
	String getServiceId();

	/**
	 * Get a set that represent the days that the service is available in them
	 */
	EnumSet<Day> getValidDays();

	/**
	 * Indicates that service is available for a given day.
	 * 
	 * @return true if service is available for all given day in the date range (The
	 *         date range is specified using the 'start date' and 'end date'
	 *         fields.)
	 */
	boolean isValid(Day day);

	/**
	 * StartDate represent the start date for the service.
	 */
	LocalDate getStartDate();

	/**
	 * EndDate represent the end date for the service.
	 */
	LocalDate getEndDate();

}
