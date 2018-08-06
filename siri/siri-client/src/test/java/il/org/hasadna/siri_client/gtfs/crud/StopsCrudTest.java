package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;

import org.junit.Before;
import org.junit.Test;

public class StopsCrudTest {

	private static String nonExistFilePath = "non_exist_file";
	private static String ExistFilePath = "src/test/resources/siri_client/gtfs/cruds/min_stops.txt";
	
	
	@Before
	public void setUp() throws Exception {
	}

	@Test(expected = IOException.class)
	public void testStopsCrud_non_exist_file() throws IOException {
		new StopsCrud(Paths.get(nonExistFilePath));
	}

	@Test
	public void testStopsCrud() throws IOException {
		new StopsCrud(Paths.get(ExistFilePath));
	}

	@Test
	public void testParseLineString() throws IOException {
		
		Stop actual = new StopsCrud(Paths.get(ExistFilePath)).parseLine("1,38831,בי''ס בר לב/בן יהודה, רחוב:בן יהודה 76 עיר: כפר סבא רציף:   קומה:  ,32.183939,34.917812,0,,6900");
		
		assertEquals(0, actual.getLocationType());
		assertEquals(0, actual.getParentStation());
		assertEquals(38831, actual.getStopCode());
		assertEquals(" רחוב:בן יהודה 76 עיר: כפר סבא רציף:   קומה:  ", actual.getStopDesc());
		assertEquals(1, actual.getStopId());
		assertEquals(32.183939, actual.getStopLat(), 0);
		assertEquals(34.917812, actual.getStopLon(), 0);
		assertEquals("בי''ס בר לב/בן יהודה", actual.getStopName());
		assertEquals(6900, actual.getZoneId());
	}

}
