package il.org.hasadna.siri_client.gtfs.analysis;

import static org.junit.Assert.assertEquals;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumSet;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.crud.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.crud.BaseTrip;
import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public class GtfsDataManipulationsTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	private static final LocalDate BEFORE_DATE = LocalDate.ofYearDay(2000, 14);
	private static final LocalDate AFTER_DATE = LocalDate.ofYearDay(2000, 16);
	private static final LocalDate CURRENT_DATE = LocalDate.ofYearDay(2000, 15);
	private GtfsCrud gtfsCrud;

	@Before
	public void setUp() throws Exception {

		GtfsZipFile gtfsZipFile = new GtfsZipFile(Paths.get("src/test/resources/siri_client/gtfs/cruds/cruds.zip"));
		gtfsCrud = new GtfsCrud(gtfsZipFile);

	}

	@Test(expected = NullPointerException.class)
	public void testGtfsDataManipulations() {
		new GtfsDataManipulations(null);
	}

	@Test
	public void testGetCalendarCrud() throws IOException {
		// Prepare
		GtfsZipFile gtfsZipFile = new GtfsZipFile(Paths.get("src/test/resources/siri_client/gtfs/cruds/cruds.zip"));

		BaseCalendar baseCalendar = new BaseCalendar(new ServiceId(""), EnumSet.noneOf(DayOfWeek.class),
				LocalDate.now(), LocalDate.now());

		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile) {
			@Override
			public Stream<Calendar> getCalendars() throws IOException {

				return Stream.of(baseCalendar);
			}
		};
		// Execute
		Stream<Calendar> resultStream = new GtfsDataManipulations(gtfsCrud).getCalendarItems();
		List<Calendar> actual = resultStream.collect(Collectors.toList());

		// Expected

		List<Calendar> expected = Arrays.asList(baseCalendar);

		assertEquals(expected, actual);

	}

	@Test
	public void testGetTripCrud() throws IOException {

		// Prepare
		GtfsZipFile gtfsZipFile = new GtfsZipFile(Paths.get("src/test/resources/siri_client/gtfs/cruds/cruds.zip"));

		BaseTrip baseTrip = new BaseTrip("routeId", new ServiceId("serviceId"), "tripId", "tripHeadsign", 0, 0);

		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile) {
			@Override
			public Stream<Trip> getTrips() throws IOException {
				return Stream.of(baseTrip);
			}
		};
		// Execute
		Stream<Trip> resultStream = new GtfsDataManipulations(gtfsCrud).getTripItems();
		List<Trip> actual = resultStream.collect(Collectors.toList());

		// Expected

		List<Trip> expected = Arrays.asList(baseTrip);

		assertEquals(expected, actual);

	}

	@Test
	public void testGetStopTimesCrud() throws IOException {

		// Prepare
		GtfsZipFile gtfsZipFile = new GtfsZipFile(Paths.get("src/test/resources/siri_client/gtfs/cruds/cruds.zip"));

		StopTime stopTime = new BaseStopTime("tripId", "arrivalTime", "departureTime", 0, 0, 0, 0, 0);
		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile) {
			@Override
			public Stream<StopTime> getStopTimes() throws IOException {
				return Stream.of(stopTime);
			}
		};
		// Execute
		Stream<StopTime> resultStream = new GtfsDataManipulations(gtfsCrud).getStopTimesItems();
		List<StopTime> actual = resultStream.collect(Collectors.toList());

		// Expected

		List<StopTime> expected = Arrays.asList(stopTime);

		assertEquals(expected, actual);

	}

	@Test
	public void testGetRelevantStopTimeItemsLocalDate() throws IOException {
		StopTime stopTime = new BaseStopTime("tripId", "arrivalTime", "departureTime", 0, 0, 0, 0, 0);

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			Stream<Calendar> getCalendarItems() throws IOException {

				BaseCalendar itm = new BaseCalendar(new ServiceId("ServiceId"), EnumSet.of(CURRENT_DATE.getDayOfWeek()),
						CURRENT_DATE, CURRENT_DATE);

				return Stream.of(itm);
			};

			@Override
			Stream<Trip> getTripItems() throws IOException {

				Trip trip = new BaseTrip("routeId", new ServiceId("ServiceId"), "tripId", "tripHeadsign", 0, 0);
				return Stream.of(trip);
			}

			@Override
			Stream<StopTime> getStopTimesItems() throws IOException {
				
				
				return Stream.of(stopTime);
			}
		};

		// Execute
		List<StopTime> actual = gtfsDataManipulations.getRelevantStopTimeItems(CURRENT_DATE).collect(Collectors.toList());

		
		// Expectes
		List<StopTime> expected = Arrays.asList(stopTime);
		
		
		assertEquals(expected , actual);

	}

	@Test
	public void testGetRelevantStopIds() throws IOException {
		StopTime stopTime = new BaseStopTime("tripId", "arrivalTime", "departureTime", 777, 0, 0, 0, 0);

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			Stream<Calendar> getCalendarItems() throws IOException {

				BaseCalendar itm = new BaseCalendar(new ServiceId("ServiceId"), EnumSet.of(CURRENT_DATE.getDayOfWeek()),
						CURRENT_DATE, CURRENT_DATE);

				return Stream.of(itm);
			};

			@Override
			Stream<Trip> getTripItems() throws IOException {

				Trip trip = new BaseTrip("routeId", new ServiceId("ServiceId"), "tripId", "tripHeadsign", 0, 0);
				return Stream.of(trip);
			}

			@Override
			Stream<StopTime> getStopTimesItems() throws IOException {
				
				
				return Stream.of(stopTime);
			}
		};

		// Execute
		 List<Integer> actual = gtfsDataManipulations.getRelevantStopIds(CURRENT_DATE).collect(Collectors.toList());

		
		// Expectes
		 List<Integer> expected = Arrays.asList(stopTime.getStopId());
		
		
		assertEquals(expected , actual);

	}

	@Test
	public void testGetRelevantCalendarItems_elem_from_currDate_to_currDate() throws IOException {

		// Prepare

		BaseCalendar baseCalendar = new BaseCalendar(new ServiceId(""), EnumSet.of(CURRENT_DATE.getDayOfWeek()),
				CURRENT_DATE, CURRENT_DATE);

		// Execute
		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			Stream<Calendar> getCalendarItems() throws IOException {
				return Stream.of(baseCalendar);
			};
		};

		Stream<Calendar> resultStream = gtfsDataManipulations.getRelevantCalendarItems(CURRENT_DATE);
		List<Calendar> actual = resultStream.collect(Collectors.toList());

		assertEquals(Arrays.asList(baseCalendar), actual);

	}

	@Test
	public void testGetRelevantCalendarItems_elem_from_currDate_to_currDate_() throws IOException {

		// Prepare
		BaseCalendar baseCalendar = new BaseCalendar(new ServiceId(""), EnumSet.of(CURRENT_DATE.getDayOfWeek()),
				CURRENT_DATE, CURRENT_DATE);

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			java.util.stream.Stream<Calendar> getCalendarItems() throws IOException {
				return Stream.of(baseCalendar);
			};
		};

		// Execute
		Stream<Calendar> resultStream = gtfsDataManipulations.getRelevantCalendarItems(CURRENT_DATE);
		List<Calendar> actual = resultStream.collect(Collectors.toList());
		// Test
		assertEquals(Arrays.asList(baseCalendar), actual);

	}

	@Test
	public void testGetRelevantCalendarItems_elem_from_non_relevant_dates() throws IOException {

		// Prepare
		BaseCalendar beforeCalendar = new BaseCalendar(new ServiceId(""), EnumSet.of(CURRENT_DATE.getDayOfWeek()),
				BEFORE_DATE, BEFORE_DATE);

		BaseCalendar afterCalendar = new BaseCalendar(new ServiceId(""), EnumSet.of(CURRENT_DATE.getDayOfWeek()),
				AFTER_DATE, AFTER_DATE);

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			java.util.stream.Stream<Calendar> getCalendarItems() throws IOException {
				return Stream.of(beforeCalendar, afterCalendar);
			};
		};

		// Execute
		Stream<Calendar> resultStream = gtfsDataManipulations.getRelevantCalendarItems(CURRENT_DATE);
		List<Calendar> actual = resultStream.collect(Collectors.toList());
		// Test
		assertEquals(Collections.emptyList(), actual);

	}

	@Test
	public void testGetRelevantCalendarItems_elem_from_non_relevant_weekday() throws IOException {

		// Prepare
		BaseCalendar beforeCalendar = new BaseCalendar(new ServiceId(""), EnumSet.of(CURRENT_DATE.getDayOfWeek()
				.plus(1)), CURRENT_DATE, CURRENT_DATE);

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			java.util.stream.Stream<Calendar> getCalendarItems() throws IOException {
				return Stream.of(beforeCalendar);
			};
		};

		// Execute
		Stream<Calendar> resultStream = gtfsDataManipulations.getRelevantCalendarItems(CURRENT_DATE);
		List<Calendar> actual = resultStream.collect(Collectors.toList());
		// Test
		assertEquals(Collections.emptyList(), actual);

	}

	@Test
	public void testGetUniqueStopTimeItems() throws IOException {

		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsCrud) {
			Stream<StopTime> getStopTimesItems() throws IOException {

				return Stream.of(new BaseStopTime("tripId", "arrivalTime", "departureTime", 0, 4, 1, 0, 45),
						new BaseStopTime("tripId", "arrivalTime", "departureTime", 0, 5, 1, 0, 45),
						new BaseStopTime("tripId", "arrivalTime", "departureTime", 0, 6, 1, 0, 45),
						new BaseStopTime("tripId", "arrivalTime", "departureTime", 0, 7, 1, 0, 45));
			}
		};

		long actual = gtfsDataManipulations.getLastStopTimeItems()
				.count();

		long expected = 1;

		assertEquals(expected, actual);

	}

}
