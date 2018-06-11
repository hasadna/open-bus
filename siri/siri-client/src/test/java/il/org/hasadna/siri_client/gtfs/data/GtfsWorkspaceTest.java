package il.org.hasadna.siri_client.gtfs.data;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.Before;
import org.junit.Test;

public class GtfsWorkspaceTest {

	private static final Path WORKSPCE_PATH = Paths
			.get("src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace");
	private GtfsWorkspace gtfsWorkspaceStub;

	@Before
	public void setUp() throws Exception {

		gtfsWorkspaceStub = new GtfsWorkspace(WORKSPCE_PATH) {
			@Override
			Path extractFile(String fileName, String fileLable) throws IOException {
				return Files.createTempFile(null, null);
			}
		};

	}

	@Test
	public void testGetWorkspacePath() {

		Path actual = gtfsWorkspaceStub.getWorkspacePath();
		Path expected = WORKSPCE_PATH;

		assertEquals(expected, actual);
	}

	@Test
	public void testGetCalendarFile() throws IOException {

		Path actual = gtfsWorkspaceStub.getCalendarFile();

		assertEquals("second call for getCalendarFile rsults with other path", actual,
				gtfsWorkspaceStub.getCalendarFile());
	}

	@Test
	public void testGetStopTimeFile() throws IOException {

		Path actual = gtfsWorkspaceStub.getStopTimeFile();

		assertEquals("second call for getStopTimeFile rsults with other path", actual,
				gtfsWorkspaceStub.getStopTimeFile());
	}

	@Test
	public void testGetTripsFile() throws IOException {

		Path actual = gtfsWorkspaceStub.getTripsFile();

		assertEquals("Second call for getTripsFile rsults with other path", actual, gtfsWorkspaceStub.getTripsFile());
	}

	@Test
	public void testExtractFile() throws IOException {
		// Prepare
		GtfsWorkspace gtfsWorkspace = new GtfsWorkspace(WORKSPCE_PATH);
		// Execute
		Path actual = gtfsWorkspace.extractFile(GtfsWorkspace.CALENDAR_FILE_NAME, null);
		// Test
		assertTrue("The file is not exists", Files.exists(actual));
		assertTrue("The file is empty", !Files.readAllLines(actual).isEmpty());
	}

}
