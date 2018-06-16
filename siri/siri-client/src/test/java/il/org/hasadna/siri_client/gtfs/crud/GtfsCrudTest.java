package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public class GtfsCrudTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void test_files_with_content() throws IOException {

		GtfsZipFile gtfsZipFile = new GtfsZipFile(Paths.get("src/test/resources/siri_client/gtfs/cruds/cruds.zip"));

		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile);
		Trip tripsActual = gtfsCrud.getTrips()
				.findAny()
				.get();
		Calendar calendarsActual = gtfsCrud.getCalendars()
				.findAny()
				.get();
		StopTime stopTimesActual = gtfsCrud.getStopTimes()
				.findAny()
				.get();

		assertNotNull(tripsActual);
		assertNotNull(calendarsActual);
		assertNotNull(stopTimesActual);
	}

	@Test
	public void test_files_WITHOUT_content() throws IOException {

		GtfsZipFile gtfsZipFile = new GtfsZipFile(
				Paths.get("src/test/resources/siri_client/gtfs/cruds/cruds_empty.zip"));

		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile);

		boolean tripsActual = gtfsCrud.getTrips()
				.findAny()
				.isPresent();

		boolean calendarsActual = gtfsCrud.getCalendars()
				.findAny()
				.isPresent();
		boolean stopTimesActual = gtfsCrud.getStopTimes()
				.findAny()
				.isPresent();

		assertFalse(tripsActual);
		assertFalse(calendarsActual);
		assertFalse(stopTimesActual);
	}

}
