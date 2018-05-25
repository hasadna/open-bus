package il.org.hasadna.siri_client.gtfs;

import static org.junit.Assert.*;

import java.time.LocalDate;
import java.util.EnumSet;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.Calendar.Day;

public class BaseCalendarTest {
	private static final String SERVICE_ID = "SERVICE_ID";
	private static final EnumSet<Day> VALID_DAYS = EnumSet.of(Calendar.Day.SUNDAY, Calendar.Day.MONDAY,
			Calendar.Day.TUESDAY);
	private static final LocalDate START_DATE = LocalDate.of(2017, 1, 1);
	private static final LocalDate END_DATE = LocalDate.of(2018, 1, 1);

	BaseCalendar baseCalendar;

	@Before
	public void setUp() throws Exception {
		baseCalendar = new BaseCalendar(SERVICE_ID, VALID_DAYS, START_DATE, END_DATE);
	}

	 @Test (expected = IllegalArgumentException.class)
	 public void testParse_argument_err() {
		 BaseCalendar.parse("");
	 }
	 
	 @Test 
	 public void testParse() {
		 BaseCalendar actual = BaseCalendar.parse("59923056,0,0,0,0,0,1,0,20180608,20180613");
		 assertEquals("59923056", actual.getServiceId());
		 assertEquals(EnumSet.of(Calendar.Day.FRIDAY), actual.getValidDays());
		 assertEquals(LocalDate.of(2018, 6, 8), actual.getStartDate());
		 assertEquals(LocalDate.of(2018, 6, 13), actual.getEndDate());
	 }

	@Test
	public void testGetServiceId() {
		String expected = SERVICE_ID;
		String actual = baseCalendar.getServiceId();
		assertEquals(expected, actual);
		
	}

	@Test
	public void testGetValidDays() {
		EnumSet<Day> expected = VALID_DAYS;
		EnumSet<Day>  actual = baseCalendar.getValidDays();
		assertEquals(expected, actual);
		
	}

	@Test
	public void testIsValid_true() {
		 boolean expected = true;
		 boolean actual = baseCalendar.isValid(Day.SUNDAY);
		 assertEquals(expected, actual);
	}

	@Test
	public void testIsValid_false() {
		 boolean expected = false;
		 boolean actual = baseCalendar.isValid(Day.SATURDAY);
		 assertEquals(expected, actual);
	}

	@Test
	public void testGetStartDate() {
		 LocalDate expected = START_DATE;
		 LocalDate  actual = baseCalendar.getStartDate();
		assertEquals(expected, actual);
			}

	@Test
	public void testGetEndDate() {
		 LocalDate expected = END_DATE;
		 LocalDate  actual = baseCalendar.getEndDate();
		assertEquals(expected, actual);
			}

}
