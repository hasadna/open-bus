package il.org.hasadna.siri_client.gtfs.crud;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Objects;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class GtfsZipFile {
	static final String CALENDAR_FILE_NAME = "calendar.txt";
	static final String STOP_TIME_FILE_NAME = "stop_times.txt";
	static final String TRIPS_FILE_NAME = "trips.txt";
	Path gtfsZip;

	public GtfsZipFile(Path gtfsZip) {
		this.gtfsZip = Objects.requireNonNull(gtfsZip, "gtfsZip is null");
	}

	public Path getGtfsZip() {
		return gtfsZip;
	}

	/**
	 * Extracts a ZIP entry (file name) to temporary file
	 * 
	 * @param fileName
	 *            The name of the entry in ZIP file
	 * @param fileLable
	 *            String to be used in generating the file's name; may be null
	 * @return The path to the newly extracted file
	 * @throws IOException
	 */
	Path extractFile(String fileName, String fileLable) throws IOException {
		ZipFile d = new ZipFile(getGtfsZip().toFile());
		InputStream in = getFileInStream(d, fileName);
		Path dest = Files.createTempFile(fileLable, ".txt");
		Files.copy(in, dest, StandardCopyOption.REPLACE_EXISTING);
		d.close();
		return dest;

	}

	InputStream getFileInStream(ZipFile zipFile, String entryFileName) throws IOException {
		ZipEntry entry = zipFile.getEntry(entryFileName);
		if (entry == null) {
			throw new FileNotFoundException("can't find the file: [" + entryFileName + "] in the zip file");
		}
		return zipFile.getInputStream(entry);
	}

	public Path extractCalendarFile() throws IOException {

		return extractFile(CALENDAR_FILE_NAME, null);
	}

	public Path extractTripsFile() throws IOException {

		return extractFile(TRIPS_FILE_NAME, null);
	}

	public Path extractStopTimesFile() throws IOException {

		return extractFile(STOP_TIME_FILE_NAME, null);
	}
}
