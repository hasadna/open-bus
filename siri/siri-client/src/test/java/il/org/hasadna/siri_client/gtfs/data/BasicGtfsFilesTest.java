package il.org.hasadna.siri_client.gtfs.data;

import static org.junit.Assert.*;

import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.Before;
import org.junit.Test;

public class BasicGtfsFilesTest {
	static Path calendarFile = Paths.get("calendar");
	static Path stopTimeFile = Paths.get("stopTimes");
	static Path tripsFile = Paths.get("trips");
	private BasicGtfsFiles basicGtfsFiles;

	@Before
	public void setUp() throws Exception {
		basicGtfsFiles = new BasicGtfsFiles(calendarFile, stopTimeFile, tripsFile);
		
	}

	@Test (expected=NullPointerException.class)
	public void testBasicGtfsFiles() {
		new BasicGtfsFiles(null, null, null);
	}

	@Test
	public void testGetCalendarFile()  {
		// Execute
		Path actual = basicGtfsFiles.getCalendarFile();
		// Expected
		Path expected = calendarFile;
		// Test
		assertEquals(expected, actual);
	}

	@Test
	public void testGetStopTimeFile() {
		// Execute
		Path actual = basicGtfsFiles.getStopTimeFile();
		// Expected
		Path expected = stopTimeFile;
		// Test
		assertEquals(expected, actual);
		}

	@Test
	public void testGetTripsFile() {
		// Execute
		Path actual = basicGtfsFiles.getTripsFile();
		// Expected
		Path expected = tripsFile;
		// Test
		assertEquals(expected, actual);
		}

}
