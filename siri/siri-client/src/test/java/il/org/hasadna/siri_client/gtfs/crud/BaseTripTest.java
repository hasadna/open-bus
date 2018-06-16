package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.BaseTrip;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import il.org.hasadna.siri_client.gtfs.crud.Trip;
import nl.jqno.equalsverifier.EqualsVerifier;

public class BaseTripTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testParse() {

		Trip baseTrip = BaseTrip.parse("1,59884326,27727657_210518,רכבת מזרח/שוק,0,94990");

		// assertEquals(null, baseTrip.getColor());
		assertEquals(0, baseTrip.getDirectionId());
		assertEquals("1", baseTrip.getRouteId());
		assertEquals(new ServiceId("59884326"), baseTrip.getServiceId());
		assertEquals(94990, baseTrip.getShapeId());
		assertEquals("רכבת מזרח/שוק", baseTrip.getTripHeadsign());
		assertEquals("27727657_210518", baseTrip.getTripId());

	}

	@Test
	public void testParse_empty_shapeId_field() {

		Trip baseTrip = BaseTrip.parse("1,59884326,27727657_210518,רכבת מזרח/שוק,0,");

		assertEquals(0, baseTrip.getShapeId());

	}

	@Test
	public void testEquals() {
		EqualsVerifier.forClass(BaseTrip.class).verify();
		;
	}

}
