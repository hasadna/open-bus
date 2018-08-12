package il.org.hasadna.siri_client.gtfs.analysis;

import java.io.IOException;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import il.org.hasadna.siri_client.gtfs.crud.*;
import il.org.hasadna.siri_client.gtfs.crud.Calendar;

public class GtfsDataManipulations {

	private GtfsCrud gtfsCrud;

	private Map<ServiceId, Calendar> calendars;
	private Map<String, Trip> trips;
	private Map<String, List<StopTime>> stopTimes;
	private Map<Integer, Stop> stops;
	private Map<String, Route> routes;

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

	public Map<String, Route> getRoutes() {
		return routes;
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

		routes = filterRoutes(trips);
	}

	private Map<String,Route> filterRoutes(Map<String, Trip> trips) throws IOException {
		Set<String> routesOfTrips = trips.values().stream().map(tr -> tr.getRouteId()).collect(Collectors.toSet());
		Map<String, Route> routesByRouteId
				= getGtfsCrud().getRoutes().
				filter(r -> routesOfTrips.contains(r.getRouteId())).
				collect(Collectors.toMap(Route::getRouteId, r -> r));
		return routesByRouteId;
//		Map<String, List<Trip>> tripsByRouteId = trips.values().stream().collect(Collectors.groupingBy(Trip::getRouteId));
//		Map<String, Route> routesByTripId = new HashMap<>();
//		for (String routeId : tripsByRouteId.keySet()) {
//			tripsByRouteId.get(routeId).forEach( trip ->
//					routesByTripId.put(trip.getTripId(), routesByRouteId.get(routeId))
//			);
//		}
//		return routesByTripId;
	}

	public Collection<GtfsRecord> combine(LocalDate date) throws IOException {
		filterGtfs(date);
		return getTrips().values().stream().map(this::createGtfsRecord).collect(Collectors.toList());
	}

	public Collection<GtfsRecord> combineForSpecificRoute(LocalDate date, String routeId) throws IOException {
		filterGtfs(date);
		return getTrips().values().stream()
				.filter(trip-> trip.getRouteId().equals(routeId))
				.map(this::createGtfsRecord).collect(Collectors.toList());
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
