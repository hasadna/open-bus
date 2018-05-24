package il.org.hasadna.siri_client.gtfs.cruds;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.BaseTrip;
import il.org.hasadna.siri_client.gtfs.Trip;
import il.org.hasadna.siri_client.gtfs.cruds.TripCrud;

public class TripCrudTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testReadAll() throws IOException {
		List<Trip> actual = new TripCrud(Paths.get("src/test/resources/siri_client/gtfs/cruds/min_trips.txt")).ReadAll()
				.collect(Collectors.toList());

		List<Trip> expected = Arrays.asList(BaseTrip.parse("1,59884325,27727521_210518,רכבת מזרח/שוק,0,94990"),
				BaseTrip.parse("1,59884325,27727524_210518,רכבת מזרח/שוק,0,94990"),
				BaseTrip.parse("1,59884325,27727528_210518,רכבת מזרח/שוק,0,94990"));

		assertEquals(expected, actual);

	}



}
