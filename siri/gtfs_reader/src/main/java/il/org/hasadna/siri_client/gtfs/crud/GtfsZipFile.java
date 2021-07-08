package il.org.hasadna.siri_client.gtfs.crud;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Objects;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class GtfsZipFile {

	static final String CALENDAR_FILE_NAME = "calendar.txt";
	static final String STOP_TIME_FILE_NAME = "stop_times.txt";
	static final String TRIPS_FILE_NAME = "trips.txt";
	static final String STOPS_FILE_NAME = "stops.txt";
	static final String ROUTES_FILE_NAME = "routes.txt";

	private Path gtfsZip;

	public GtfsZipFile(Path gtfsZip) {
		this.gtfsZip = Objects.requireNonNull(gtfsZip, "gtfsZip is null");
	}

	/**
	 * Extracts a ZIP entry (file name) to temporary file
	 *
	 * @param fileName The name of the entry in ZIP file
	 * @param extractTo String to be used in generating the file's name; may be null
	 * @return The path to the newly extracted file
	 * @throws IOException if an I/O error occurs when reading or writing
	 */
	public void extractFile(String fileName, Path extractTo) throws IOException {
		try (ZipFile d = new ZipFile(gtfsZip.toFile())) {
			InputStream in = getFileInStream(d, fileName);

			Files.copy(in, extractTo, StandardCopyOption.REPLACE_EXISTING);
		}
	}

	private Path extractFile(String fileName) throws IOException {
		try (ZipFile d = new ZipFile(gtfsZip.toFile())) {
			InputStream in = getFileInStream(d, fileName);

			Path dest = Paths.get(GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory(), fileName);

			Files.copy(in, dest, StandardCopyOption.REPLACE_EXISTING);

			return dest;
		}
	}

	InputStream getFileInStream(ZipFile zipFile, String entryFileName) throws IOException {
		ZipEntry entry = zipFile.getEntry(entryFileName);
		if (entry == null) {
			throw new FileNotFoundException("can't find the file: [" + entryFileName + "] in the zip file");
		}
		return zipFile.getInputStream(entry);
	}


	/**
	 * @return Path to the extracted Calendar file
	 * @throws IOException if an I/O error occurs when reading or writing
	 */
	public Path extractCalendarFile() throws IOException {
		return extractFile(CALENDAR_FILE_NAME);
	}

	/**
	 * @return Path to the extracted Trips file
	 * @throws IOException if an I/O error occurs when reading or writing
	 */
	public Path extractTripsFile() throws IOException {

		return extractFile(TRIPS_FILE_NAME);
	}

	/**
	 * @return Path to the extracted StopTimes file
	 * @throws IOException if an I/O error occurs when reading or writing
	 */
	public Path extractStopTimesFile() throws IOException {

		return extractFile(STOP_TIME_FILE_NAME);
	}

	/**
	 * @return Path to the extracted Stops file
	 * @throws IOException if an I/O error occurs when reading or writing
	 */
	public Path extractStopsFile() throws IOException {

		return extractFile(STOPS_FILE_NAME);
	}

	public Path extractRoutesFile() throws IOException {

		return extractFile(ROUTES_FILE_NAME);
	}

}
