package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import nl.jqno.equalsverifier.EqualsVerifier;

public class ServiceIdTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testEqualsObject() {
		EqualsVerifier.forClass(ServiceId.class).verify();
	}

	
	@Test
	public void testToString() {
		ServiceId serviceId = new ServiceId("MyServiceId");
		String actual = serviceId.toString();
		String expected = "ServiceId [serviceId=MyServiceId]";
		assertEquals(expected, actual);
	}

}
