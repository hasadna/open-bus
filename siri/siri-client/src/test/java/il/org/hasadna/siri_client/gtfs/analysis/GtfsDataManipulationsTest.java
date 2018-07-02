package il.org.hasadna.siri_client.gtfs.analysis;

import static org.junit.Assert.assertEquals;

//import static org.junit.Assert.*;

import java.io.IOException;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collection;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.crud.BaseStop;
import il.org.hasadna.siri_client.gtfs.crud.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.crud.BaseTrip;
import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.Crud;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import il.org.hasadna.siri_client.gtfs.crud.Stop;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public class GtfsDataManipulationsTest {
	public static GtfsCrud emptyGtfsCrud = new GtfsCrud(new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>(),
			new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>());

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public final void testFilterCalendars_filter_by_date_find_item() throws IOException {
		// Prepare
		LocalDate currentDate = LocalDate.of(2018, 1, 1);
		/* creating 5 calendar items */
		BaseCalendar calendarToFind = new BaseCalendar(new ServiceId("ServiceId"), EnumSet.allOf(DayOfWeek.class),
				currentDate.minusDays(1), currentDate.plusDays(1));

		BaseCalendar otherCalendarToFind = new BaseCalendar(new ServiceId("ServiceId"), EnumSet.allOf(DayOfWeek.class),
				currentDate, currentDate);

		BaseCalendar calendarOfOtherDayOfWeek = new BaseCalendar(new ServiceId("ServiceId"),
				EnumSet.of(currentDate.getDayOfWeek().plus(1)), currentDate.minusDays(1), currentDate.plusDays(1));

		BaseCalendar bigerCalendar = new BaseCalendar(new ServiceId("ServiceId"), EnumSet.allOf(DayOfWeek.class),
				currentDate.plusDays(1), currentDate.plusDays(2));

		BaseCalendar smallerCalendar = new BaseCalendar(new ServiceId("ServiceId"), EnumSet.allOf(DayOfWeek.class),
				currentDate.minusDays(2), currentDate.minusDays(1));
		/* create calendar CRUD that read the 3 items */
		Crud<Calendar> calendarCrud = new Crud<Calendar>() {
			@Override
			public Stream<Calendar> ReadAll() throws IOException {
				return Stream.of(calendarToFind, bigerCalendar, smallerCalendar, calendarOfOtherDayOfWeek,
						otherCalendarToFind);
			}
		};
		/* create gtfs CRUD with the calendar CRUD and the other CRUD as empty CRUDs */
		GtfsCrud gtfsCrud = new GtfsCrud(new Crud.EmptyCrud<>(), calendarCrud, new Crud.EmptyCrud<>(),
				new Crud.EmptyCrud<>());

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud);

		// Expected
		Collection<Calendar> expected = new HashSet<>(Arrays.asList(calendarToFind, otherCalendarToFind));

		// Execute
		Collection<Calendar> actual = new HashSet<>(gtfsDataManipulations.filterCalendars(currentDate));
		// Test
		assertEquals(expected, actual);
	}

	@Test
	public final void testFilterTrips_filter_by_serviceID() throws IOException {
		// Prepare
		BaseTrip tripToFind = new BaseTrip("routeId", new ServiceId("foo"), "tripId", "tripHeadsign", 0, 0);
		BaseTrip otherTrip = new BaseTrip("routeId", new ServiceId("bar"), "tripId", "tripHeadsign", 0, 0);

		GtfsCrud gtfsCrud = new GtfsCrud(new Crud<Trip>() {

			@Override
			public Stream<Trip> ReadAll() throws IOException {
				return Stream.of(tripToFind, otherTrip);
			}

		}, new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>());

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud);
		Set<ServiceId> ServiceIds = new HashSet<>(Arrays.asList(new ServiceId("foo")));

		// Execute
		Collection<Trip> actual = gtfsDataManipulations.filterTrips(ServiceIds);
		// Expected
		Collection<Trip> expected = Arrays.asList(tripToFind);
		// Test
		assertEquals(expected, actual);

	}

	@Test
	public final void testFilterStopTimes() throws IOException {
		// Prepare
		String tripId = "foo";

		Set<String> tripIds = new HashSet<String>(Arrays.asList(tripId));

		StopTime first = new BaseStopTime("foo", "arrivalTime", "departureTime", 0, 0, 0, 0, 0);
		StopTime second = new BaseStopTime("foo", "arrivalTime", "departureTime", 0, 1, 0, 0, 0);
		StopTime last = new BaseStopTime("foo", "arrivalTime", "departureTime", 0, 1, 0, 0, 0);
		StopTime other = new BaseStopTime("bar", "arrivalTime", "departureTime", 0, 0, 0, 0, 0);

		Crud<StopTime> stopTimeCrud = new Crud<StopTime>() {

			@Override
			public Stream<StopTime> ReadAll() throws IOException {

				return Stream.of(first, second, last, other);
			}

		};

		GtfsCrud GtfsCrud = new GtfsCrud(new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>(), stopTimeCrud,
				new Crud.EmptyCrud<>());

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(GtfsCrud);
		// Execute
		Collection<StopTime> actual = gtfsDataManipulations.filterStopTimes(tripIds);
		// Expected
		Collection<StopTime> expected = Arrays.asList(first, last);
		// Test
		assertEquals(new HashSet<>(expected), new HashSet<>(actual));
	}

	@Test
	public final void testFilterStops() throws IOException {

		Stop stopToFind = new BaseStop(111, 222, "stopName", "stopDesc", 2.2, 3.3, 2, 1, 4);

		Stop otherStop = new BaseStop(333, 222, "stopName", "stopDesc", 2.2, 3.3, 2, 1, 4);

		Crud<Stop> stopsCrud = new Crud<Stop>() {

			@Override
			public Stream<Stop> ReadAll() throws IOException {
				return Stream.of(stopToFind, otherStop);
			}

		};
		GtfsCrud gtfsCrud = new GtfsCrud(new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>(), new Crud.EmptyCrud<>(),
				stopsCrud);
		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud);

		Set<Integer> tripIDs = new HashSet<>(Arrays.asList(111));

		Collection<Stop> actual = gtfsDataManipulations.filterStops(tripIDs);

		Collection<Stop> expected = Arrays.asList(stopToFind);

		assertEquals(expected, actual);
	}

	@Test
	public final void testFilterGtfs_check_the_saved_format() throws IOException {

		// Prepare

		ServiceId serviceId = new ServiceId("ServiceId");
		LocalDate currentDate = LocalDate.of(2018, 1, 1);
		BaseCalendar calendar = new BaseCalendar(serviceId, EnumSet.allOf(DayOfWeek.class), currentDate.minusDays(1),
				currentDate.plusDays(1));

		String tripId = "foo";
		int firstStopId = 111;
		int lastStopId = 333;

		StopTime firstStopTime = new BaseStopTime("foo", "arrivalTime", "departureTime", firstStopId, 0, 0, 0, 0);
		StopTime lastStopTime = new BaseStopTime("foo", "arrivalTime", "departureTime", lastStopId, 10, 0, 0, 0);

		Stop firstStop = new BaseStop(firstStopId, 222, "stopName", "stopDesc", 2.2, 3.3, 2, 1, 4);
		Stop lastStop = new BaseStop(lastStopId, 222, "stopName", "stopDesc", 2.2, 3.3, 2, 1, 4);

		BaseTrip trip = new BaseTrip("routeId", serviceId, tripId, "tripHeadsign", 0, 0);

		GtfsCrud GtfsCrud = new GtfsCrud(new Crud<Trip>() {
			@Override
			public Stream<Trip> ReadAll() throws IOException {
				return Stream.of(trip);
			}

		}, new Crud<Calendar>() {

			@Override
			public Stream<Calendar> ReadAll() throws IOException {
				return Stream.of(calendar);
			}

		}, new Crud<StopTime>() {

			@Override
			public Stream<StopTime> ReadAll() throws IOException {
				return Stream.of(firstStopTime, lastStopTime);
			}

		}, new Crud<Stop>() {

			@Override
			public Stream<Stop> ReadAll() throws IOException {
				return Stream.of(firstStop, lastStop);
			}

		});

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(GtfsCrud);

		// Execute

		gtfsDataManipulations.filterGtfs(currentDate);

		// Test Calendar
		Map<ServiceId, Calendar> actualCalendars = gtfsDataManipulations.getCalendars();

		Map<ServiceId, Calendar> expectCalendars = new HashMap<>();
		expectCalendars.put(serviceId, calendar);

		assertEquals(expectCalendars, actualCalendars);

		// Test Trips

		Map<String, Trip> actualTrips = gtfsDataManipulations.getTrips();

		Map<String, Trip> expecedTrips = new HashMap<>();
		expecedTrips.put(tripId, trip);

		assertEquals(expecedTrips, actualTrips);

		// Test StopTime

		Map<String, List<StopTime>> actualStopTimesMap = gtfsDataManipulations.getStopTimes();
		HashSet<StopTime> actualStopTimes = new HashSet<>(actualStopTimesMap.get(tripId));
		Map<String, List<StopTime>> expectedStopTimesMap = new HashMap<>();
		expectedStopTimesMap.put(tripId, Arrays.asList(firstStopTime, lastStopTime));
		HashSet<StopTime> expectedStopTimes = new HashSet<>(expectedStopTimesMap.get(tripId));

		assertEquals(expectedStopTimes, actualStopTimes);

		// Test Stop
		Map<Integer, Stop> actualStops = gtfsDataManipulations.getStops();

		Map<Integer, Stop> expectedStops = new HashMap<>();
		expectedStops.put(firstStopId, firstStop);
		expectedStops.put(lastStopId, lastStop);

		assertEquals(expectedStops, actualStops);

	}

}
