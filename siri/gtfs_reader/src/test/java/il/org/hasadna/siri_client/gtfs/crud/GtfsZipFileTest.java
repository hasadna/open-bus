package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.zip.ZipFile;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;

public class GtfsZipFileTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@Before
	public void setUp() throws Exception {
	}

	@Test(expected = NullPointerException.class)
	public void testGtfsZipFile_of_null() {

		new GtfsZipFile(null);
	}

	@Test
	public void testGetGtfsZip() {

		Path expected = Paths.get("foo_bar");

		GtfsZipFile gtfsZipFile = new GtfsZipFile(expected);
		Path actual = gtfsZipFile.getGtfsZip();

		assertEquals(expected, actual);
	}

	@Test
	public void testExtractFile() throws IOException {
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		Path extractedFile = gtfsZipFile.extractFile("calendar.txt", null);
		String actual = new String(Files.readAllBytes(extractedFile));
		// Expected
		String expected = "foo bar";
		// Test
		assertEquals(expected, actual);
	}

	@Test(expected = FileNotFoundException.class)
	public void testExtractFile_non_exist_entry() throws IOException {
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		gtfsZipFile.getFileInStream(new ZipFile(zipFile.toFile()), "non_exist.txt");
	}

	@Test
	public void testExtractFile_exist_entry() throws IOException {
		// Expected
		String expected = "foo bar";
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		InputStream in = gtfsZipFile.getFileInStream(new ZipFile(zipFile.toFile()), "calendar.txt");
		// Test
		String actual = new BufferedReader(new InputStreamReader(in)).readLine();
		assertEquals(expected, actual);
	}

	@Test
	public void testGetCalendarFile() throws IOException {
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		Path actual = gtfsZipFile.extractCalendarFile();
		// Test
		assertNotNull(actual);
		Files.isReadable(actual);
		assertEquals("foo bar", new String(Files.readAllBytes(actual)));
	}

	@Test
	public void testGetTripsFile() throws IOException {
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		Path actual = gtfsZipFile.extractTripsFile();
		// Test
		assertNotNull(actual);
	}

	@Test
	public void testGetStopTimesFile() throws IOException {
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		Path actual = gtfsZipFile.extractStopTimesFile();
		// Test
		assertNotNull(actual);
	}

	@Test
	public void testGetStopsFile() throws IOException {
		// Prepare
		Path zipFile = Paths.get(
				"src/test/resources/siri_client/gtfs/data/GtfsWorkspaceTest/ftpWorkspace/israel-public-transportation.zip");
		GtfsZipFile gtfsZipFile = new GtfsZipFile(zipFile);
		// Execute
		Path actual = gtfsZipFile.extractStopsFile();
		// Test
		assertNotNull(actual);
	}
}
