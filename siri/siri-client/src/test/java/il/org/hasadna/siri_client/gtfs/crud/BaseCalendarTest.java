package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.EnumSet;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;

public class BaseCalendarTest {
	private static final ServiceId SERVICE_ID = new ServiceId("SERVICE_ID");
	private static final EnumSet<DayOfWeek> VALID_DAYS = EnumSet.of(DayOfWeek.SUNDAY, DayOfWeek.MONDAY,
			DayOfWeek.TUESDAY);
	private static final LocalDate START_DATE = LocalDate.of(2017, 1, 1);
	private static final LocalDate END_DATE = LocalDate.of(2018, 1, 1);

	BaseCalendar baseCalendar;

	@Before
	public void setUp() throws Exception {
		baseCalendar = new BaseCalendar(SERVICE_ID, VALID_DAYS, START_DATE, END_DATE);
	}

	@Test(expected = IllegalArgumentException.class)
	public void testParse_argument_err() {
		BaseCalendar.parse("");
	}

	@Test
	public void testParse() {
		BaseCalendar actual = BaseCalendar.parse("59923056,0,0,0,0,0,1,0,20180608,20180613");
		assertEquals(new ServiceId("59923056"), actual.getServiceId());
		assertEquals(EnumSet.of(DayOfWeek.FRIDAY), actual.getValidDays());
		assertEquals(LocalDate.of(2018, 6, 8), actual.getStartDate());
		assertEquals(LocalDate.of(2018, 6, 13), actual.getEndDate());
	}

	@Test
	public void testGetServiceId() {
		ServiceId expected = SERVICE_ID;
		ServiceId actual = baseCalendar.getServiceId();
		assertEquals(expected, actual);

	}

	@Test
	public void testGetValidDays() {
		EnumSet<DayOfWeek> expected = VALID_DAYS;
		EnumSet<DayOfWeek> actual = baseCalendar.getValidDays();
		assertEquals(expected, actual);

	}

	@Test
	public void testIsValid_true() {
		boolean expected = true;
		boolean actual = baseCalendar.isDayValid(DayOfWeek.SUNDAY);
		assertEquals(expected, actual);
	}

	@Test
	public void testIsValid_false() {
		boolean expected = false;
		boolean actual = baseCalendar.isDayValid(DayOfWeek.SATURDAY);
		assertEquals(expected, actual);
	}

	@Test
	public void testGetStartDate() {
		LocalDate expected = START_DATE;
		LocalDate actual = baseCalendar.getStartDate();
		assertEquals(expected, actual);
	}

	@Test
	public void testGetEndDate() {
		LocalDate expected = END_DATE;
		LocalDate actual = baseCalendar.getEndDate();
		assertEquals(expected, actual);
	}
	
	
	
	@Test
	public void tmp() throws IOException {
		
		InputStream in = ClassLoader.getSystemClassLoader().getResourceAsStream("sdf.tmp");
		Path dest = Files.createTempFile(null, null);
		Files.copy(in, dest,StandardCopyOption.REPLACE_EXISTING);
		System.out.println(dest);
	}

}
