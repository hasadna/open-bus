package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.EnumSet;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.CalendarCrud;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;

public class CalendarCrudTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testParseLineString() throws IOException {
		CalendarCrud calendarCrud = new CalendarCrud(
				Paths.get("src/test/resources/siri_client/gtfs/cruds/min_calendar.txt"));
		assertEquals(7, calendarCrud.ReadAll().count());

	}

	@Test
	public void testgetRelevantCalendarItems() throws IOException {
		// prepare
		BaseCalendar c1 = new BaseCalendar(new ServiceId("1"), EnumSet.of(DayOfWeek.SUNDAY, DayOfWeek.MONDAY),
				LocalDate.of(2017, 1, 1), LocalDate.of(2018, 1, 1));
		BaseCalendar c2 = new BaseCalendar(new ServiceId("2"), EnumSet.of(DayOfWeek.SUNDAY), LocalDate.of(2017, 1, 1),
				LocalDate.of(2018, 1, 1)); // wrong day
		BaseCalendar c3 = new BaseCalendar(new ServiceId("3"), EnumSet.of(DayOfWeek.SUNDAY, DayOfWeek.THURSDAY),
				LocalDate.of(2017, 1, 1), LocalDate.of(2018, 1, 1)); // // wrong day
		BaseCalendar c4 = new BaseCalendar(new ServiceId("4"), EnumSet.of(DayOfWeek.SUNDAY), LocalDate.of(2017, 1, 1),
				LocalDate.of(2017, 4, 1)); // not in dates range
		BaseCalendar c5 = new BaseCalendar(new ServiceId("5"), EnumSet.of(DayOfWeek.SUNDAY), LocalDate.of(2017, 6, 1),
				LocalDate.of(2018, 1, 1));// not in dates range

		CalendarCrud calendarCrud = new CalendarCrud(
				Paths.get("src/test/resources/siri_client/gtfs/cruds/min_calendar.txt")) {
			@Override
			public Stream<Calendar> ReadAll() throws IOException {
				return Arrays.asList(c1, c2, c3, c4, c5).stream().map(i -> (Calendar) i);
			}
		};

		LocalDate currentDate = LocalDate.of(2017, 5, 1); // Monday

		// expected
		List<BaseCalendar> expected = Arrays.asList(c1);

		// Execute
		List<Calendar> actual = calendarCrud.getRelevantCalendarItems(currentDate).collect(Collectors.toList());

		// Test
		assertEquals(expected, actual);

	}

}
