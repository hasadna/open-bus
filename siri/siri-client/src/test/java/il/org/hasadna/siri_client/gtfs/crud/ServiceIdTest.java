package il.org.hasadna.siri_client.gtfs.crud;

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

}
