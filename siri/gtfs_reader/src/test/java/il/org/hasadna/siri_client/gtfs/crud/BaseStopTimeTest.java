package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseStopTime;
import nl.jqno.equalsverifier.EqualsVerifier;

public class BaseStopTimeTest {

	@Test
	public void testParse() {
		// trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type,shape_dist_traveled
		BaseStopTime baseStopTime = BaseStopTime.parse("32217742_200518,22:20:00,22:20:00,37358,1,0,1,0");

		assertEquals("32217742_200518", baseStopTime.getTripId());
		assertEquals("22:20:00", baseStopTime.getArrivalTime());
		assertEquals("22:20:00", baseStopTime.getDepartureTime());
		assertEquals(37358, baseStopTime.getStopId());
		assertEquals(1, baseStopTime.getStopSequence());
		assertEquals(0, baseStopTime.getPickupType());
		assertEquals(1, baseStopTime.getDropOffType());
		assertEquals(0, baseStopTime.getShapeDistTraveled());
	}

	@Test
	public void testParse_empty() {
		BaseStopTime baseStopTime = BaseStopTime.parse(",,,,,,,");

		assertEquals("", baseStopTime.getTripId());
		assertEquals("", baseStopTime.getArrivalTime());
		assertEquals("", baseStopTime.getDepartureTime());
		assertEquals(0, baseStopTime.getStopId());
		assertEquals(0, baseStopTime.getStopSequence());
		assertEquals(0, baseStopTime.getPickupType());
		assertEquals(0, baseStopTime.getDropOffType());
		assertEquals(0, baseStopTime.getShapeDistTraveled());
	}

	@Test
	public void testEquals() {
		EqualsVerifier.forClass(BaseStopTime.class).verify();

	}

	@Test
	public void testToString() {
		BaseStopTime baseStopTime = BaseStopTime.parse("32217742_200518,22:20:00,22:20:00,37358,1,0,1,0");
		String actual = baseStopTime.toString();
		String expected = "BaseStopTime [tripId=32217742_200518, arrivalTime=22:20:00, departureTime=22:20:00, stopId=37358, stopSequence=1, pickupType=0, dropOffType=1, shapeDistTraveled=0]";
		assertEquals(expected, actual);
	}
}
