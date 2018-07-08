package il.org.hasadna.siri_client.gtfs.analysis;

import java.io.IOException;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import il.org.hasadna.siri_client.gtfs.crud.Stop;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public class GtfsDataManipulations {

	private GtfsCrud gtfsCrud;

	private Map<ServiceId, Calendar> calendars;
	private Map<String, Trip> trips;
	private Map<String, List<StopTime>> stopTimes;
	private Map<Integer, Stop> stops;

	Map<ServiceId, Calendar> getCalendars() {
		return calendars;
	}

	Map<String, Trip> getTrips() {
		return trips;
	}

	Map<String, List<StopTime>> getStopTimes() {
		return stopTimes;
	}

	Map<Integer, Stop> getStops() {
		return stops;
	}

	public GtfsCrud getGtfsCrud() {
		return gtfsCrud;
	}

	public GtfsDataManipulations(GtfsCrud gtfsCrud) {
		this.gtfsCrud = gtfsCrud;
	}

	/**
	 * find calendars that active in a given date. The method check that the given
	 * date is between the start date and end date of the calendar and that the
	 * given date day of week is present in the calendar
	 * 
	 * @param date
	 * @return collection of relevant calendars
	 * @throws IOException
	 *             if an I/O error occurs while reading the calendars file
	 */
	Collection<Calendar> filterCalendars(LocalDate date) throws IOException {
		DayOfWeek dayOfWeek = date.getDayOfWeek();
		return getGtfsCrud().getCalendars().filter(i -> i.getStartDate().compareTo(date) <= 0)
				.filter(i -> i.getEndDate().compareTo(date) >= 0).filter(i -> i.getValidDays().contains(dayOfWeek))
				.collect(Collectors.toList());
	}

	Collection<Trip> filterTrips(Set<ServiceId> serviceIds) throws IOException {

		return getGtfsCrud().getTrips().filter(i -> serviceIds.contains(i.getServiceId())).collect(Collectors.toList());
	}

	Collection<StopTime> filterStopTimes(Set<String> tripIds) throws IOException {

		return getGtfsCrud().getStopTimes().filter(i -> tripIds.contains(i.getTripId()))
				.collect(Collectors.groupingBy(StopTime::getTripId)).values().stream().flatMap(i -> {
					StopTime max = i.stream().collect(Collectors.maxBy(Comparator.comparing(StopTime::getStopSequence)))
							.get();
					StopTime min = i.stream().collect(Collectors.minBy(Comparator.comparing(StopTime::getStopSequence)))
							.get();
					return Stream.of(max, min);
				}).collect(Collectors.toList());
	}

	Collection<Stop> filterStops(Set<Integer> stopIDs) throws IOException {

		return getGtfsCrud().getStops().filter(i -> stopIDs.contains(i.getStopId())).collect(Collectors.toList());

	}

	void filterGtfs(LocalDate date) throws IOException {
		calendars = filterCalendars(date).stream().collect(Collectors.toMap(Calendar::getServiceId, i -> i));

		trips = filterTrips(calendars.keySet()).stream().collect(Collectors.toMap(Trip::getTripId, i -> i));

		stopTimes = filterStopTimes(trips.keySet()).stream().collect(Collectors.groupingBy(StopTime::getTripId));

		stops = filterStops(stopTimes.values().stream().flatMap(Collection::stream).map(StopTime::getStopId)
				.collect(Collectors.toSet())).stream().collect(Collectors.toMap(Stop::getStopId, i -> i));
	}

	public Collection<GtfsRecord> combine(LocalDate date) throws IOException {
		filterGtfs(date);
		return getTrips().values().stream().map(this::createGtfsRecord).collect(Collectors.toList());
	}

	private GtfsRecord createGtfsRecord(Trip currTrip) {
		Calendar currCalendar = getCalendars().get(currTrip.getServiceId());

		List<StopTime> tmpStopTimes = getStopTimes().get(currTrip.getTripId());

		StopTime currLastStopTime = tmpStopTimes.stream().max(Comparator.comparing(StopTime::getStopSequence)).get();
		Stop currLastStop = getStops().get(currLastStopTime.getStopId());

		StopTime currFirstStopTime = tmpStopTimes.stream().min(Comparator.comparing(StopTime::getStopSequence)).get();
		Stop currFirstStop = getStops().get(currFirstStopTime.getStopId());
		return new GtfsRecord(currTrip, currCalendar, currFirstStopTime, currFirstStop, currLastStopTime, currLastStop);
	}

}
