package il.org.hasadna.siri_client.gtfs.analysis;

import static org.junit.Assert.*;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.EnumSet;
import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.crud.BaseStop;
import il.org.hasadna.siri_client.gtfs.crud.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.crud.BaseTrip;
import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import il.org.hasadna.siri_client.gtfs.crud.Stop;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;
import nl.jqno.equalsverifier.EqualsVerifier;

public class GtfsRecordTest {
	

	private BaseStop firstStop;
	private BaseStop lastStop;
	private BaseStopTime firstStopTime;
	private BaseStopTime lastStopTime;
	private BaseCalendar calendar;
	private BaseTrip trip;
	private GtfsRecord gtfsRecord;

	@Before
	public void setUgp() throws Exception {

		// Prepare

		ServiceId serviceId = new ServiceId("ServiceId");
		LocalDate currentDate = LocalDate.of(2018, 1, 1);

		String tripId = "foo";
		int firstStopId = 111;
		int lastStopId = 333;
		int stopCode = 222;
		int firstStopSequence = 0;
		int lastStopSequence = firstStopSequence + 1;

		/* creating calendar object that relevant to current date */
		 calendar = new BaseCalendar(serviceId, EnumSet.allOf(DayOfWeek.class), currentDate.minusDays(1),
				currentDate.plusDays(1));

		/* creating a Trip with the same service id as in Calendar */
		 trip = new BaseTrip("routeId", serviceId, tripId, "tripHeadsign", 0, 0);

		/* creating stop times with same trip is as in trip */
		 firstStopTime = new BaseStopTime(tripId, "arrivalTime", "departureTime", firstStopId, firstStopSequence, 0, 0,
				0);
		 lastStopTime = new BaseStopTime(tripId, "arrivalTime", "departureTime", lastStopId, lastStopSequence, 0, 0, 0);

		/* create stops with the same stop id as in stop time */
		 firstStop = new BaseStop(firstStopId, stopCode, "stopName", "stopDesc", 0, 0, 0, 0, 0);
		 lastStop = new BaseStop(lastStopId, stopCode, "stopName", "stopDesc", 0, 0, 0, 0, 0);

		  gtfsRecord =  new GtfsRecord(trip, calendar, firstStopTime, firstStop, lastStopTime, lastStop);

	}
	

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testEqualAndHashCode() {
		EqualsVerifier.forClass(GtfsRecord.class).verify();		
	}
	
	@Test (expected=NullPointerException.class)
	public void testGtfsRecord_null_trip() {
		new GtfsRecord(null, calendar, firstStopTime, firstStop, lastStopTime, lastStop);
	}
	
	@Test (expected=NullPointerException.class)
	public void testGtfsRecord_null_calendar() {
		new GtfsRecord(trip, null, firstStopTime, firstStop, lastStopTime, lastStop);
	}
	
	@Test (expected=NullPointerException.class)
	public void testGtfsRecord_null_firstStopTime() {
		new GtfsRecord(trip, calendar, null, firstStop, lastStopTime, lastStop);
	}
	
	@Test (expected=NullPointerException.class)
	public void testGtfsRecord_null_firstStop() {
		new GtfsRecord(trip, calendar, firstStopTime, null, lastStopTime, lastStop);
	}
	
	@Test (expected=NullPointerException.class)
	public void testGtfsRecord_null_lastStopTime() {
		new GtfsRecord(trip, calendar, firstStopTime, firstStop, null, lastStop);
	}
	
	@Test (expected=NullPointerException.class)
	public void testGtfsRecord_null_lastStop() {
		new GtfsRecord(trip, calendar, firstStopTime, firstStop, lastStopTime, null);
	}
	
	@Test
	public void testGetTrip() {
		Trip actual = gtfsRecord.getTrip();
		Trip expected = trip;
		assertEquals(expected, actual);
	}

	@Test
	public void testGetCalendar() {
		Calendar actual = gtfsRecord.getCalendar();
		Calendar expected = calendar;
		assertEquals(expected, actual);
	}

	@Test
	public void testGetFirstStopTime() {
		 StopTime actual = gtfsRecord.getFirstStopTime();
		 StopTime expected = firstStopTime;
		assertEquals(expected, actual);
		
	}

	@Test
	public void testGetFirstStop() {
		Stop actual = gtfsRecord.getFirstStop();
		Stop expected = firstStop;
		assertEquals(expected, actual);
	}

	@Test
	public void testGetLastStopTime() {
		 StopTime actual = gtfsRecord.getLastStopTime();
		 StopTime expected = lastStopTime;
		assertEquals(expected, actual);
	}

	@Test
	public void testGetLastStop() {
		Stop actual = gtfsRecord.getLastStop();
		Stop expected = lastStop;
		assertEquals(expected, actual);	
	}
}
