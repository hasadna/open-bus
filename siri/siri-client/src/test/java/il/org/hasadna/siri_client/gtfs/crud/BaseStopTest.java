package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;


import org.junit.Before;
import org.junit.Test;

public class BaseStopTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testParse() {
		Stop actual = BaseStop.Parse(
				"1,38831,בי''ס בר לב/בן יהודה, רחוב:בן יהודה 76 עיר: כפר סבא רציף:   קומה:  ,32.183939,34.917812,0,,6900");

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

	@Test
	public void testToString() {

		String actual = new BaseStop(0, 0, "stopName", "stopDesc", 3.141234, 3.141234, 0, 0, 0).toString();
		String expected = "BaseStop [stopId=0, stopCode=0, stopName=stopName, stopDesc=stopDesc, stopLat=3.141234, stopLon=3.141234, locationType=0, parentStation=0, zoneId=0]";
		assertEquals(expected, actual);

	}

}
