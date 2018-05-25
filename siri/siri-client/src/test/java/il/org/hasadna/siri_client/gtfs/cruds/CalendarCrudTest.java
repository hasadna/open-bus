package il.org.hasadna.siri_client.gtfs.cruds;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;

import org.junit.Before;
import org.junit.Test;

public class CalendarCrudTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testParseLineString() throws IOException {
		CalendarCrud calendarCrud = new CalendarCrud(Paths.get("src/test/resources/siri_client/gtfs/cruds/min_calendar.txt"));
		assertEquals(7 , calendarCrud.ReadAll().count());
	
	}

}
