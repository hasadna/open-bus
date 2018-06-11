package il.org.hasadna.siri_client.gtfs;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collection;
import java.util.EnumSet;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

public class GtfsDataTest {

	private CalendarCrud calendarCrudStub;
	private TripCrud tripCrudStub;
	private StopTimesCrud stopTimesCrudStub;

	@Before
	public void setUp() throws Exception {

		calendarCrudStub = new CalendarCrud(Paths.get(".")) {
			@Override
			public Stream<Calendar> getRelevantCalendarItems(LocalDate currentDate) throws IOException {

				return Stream.of(new BaseCalendar(new ServiceId("100"), EnumSet.noneOf(DayOfWeek.class), LocalDate.MIN,
						LocalDate.MAX));

			}
		};
		tripCrudStub = new TripCrud(Paths.get(".")) {
			@Override
			public Stream<Trip> ReadAll() throws IOException {

				return Stream.of(new BaseTrip("", new ServiceId("100"), "200", "", 0, 0));
			}
		};
		stopTimesCrudStub = new StopTimesCrud(Paths.get(".")) {
			@Override
			public Stream<StopTime> getRelevantStopTimeItems() throws IOException {

				return Stream.of(new BaseStopTime("200", "", "", 314, 5, 0, 0, 0));
			}
		};

	}

	@Test
	public void testgetRelevantStopTimeItems() throws IOException {

		Collection<StopTime> actual = new GtfsDataManipulations(calendarCrudStub, tripCrudStub, stopTimesCrudStub)
				.getRelevantStopTimeItems(LocalDate.MAX).collect(Collectors.toList());

		Collection<BaseStopTime> expected = Arrays.asList(new BaseStopTime("200", "", "", 314, 5, 0, 0, 0));

		assertEquals(expected, actual);

	}

	@Test
	public void testgetRelevantStopIds() throws IOException {

		Collection<Integer> actual = new GtfsDataManipulations(calendarCrudStub, tripCrudStub, stopTimesCrudStub)
				.getRelevantStopIds(LocalDate.MAX).collect(Collectors.toList());

		Collection<Integer> expected = Arrays.asList(314);

		assertEquals(expected, actual);

	}

	@Test
	public void testGtfsData_paths() throws IOException {

		new GtfsDataManipulations(Paths.get("."), Paths.get("."), Paths.get("."));

	}

}
