package il.org.hasadna.siri_client.gtfs.data;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.zip.ZipFile;

public class GtfsWorkspace implements GtfsFiles{

	private static final String ZIP_FILE_NAME = "israel-public-transportation.zip";
	static final String CALENDAR_FILE_NAME = "calendar.txt";
	static final String STOP_TIME_FILE_NAME = "stop_times.txt";
	static final String TRIPS_FILE_NAME = "trips.txt";

	private Path zipFIle;

	private Path calendarFile;
	private Path stopTimeFile;
	private Path tripsFile;

	private void setCalendarFile(Path calendarFile) {
		this.calendarFile = calendarFile;
	}

	private void setStopTimeFile(Path stopTimeFile) {
		this.stopTimeFile = stopTimeFile;
	}

	private void setTripsFile(Path tripsFile) {
		this.tripsFile = tripsFile;
	}

	public GtfsWorkspace(Path zipFIle) {
		this.zipFIle = zipFIle;
	}

	public Path getZipFIle() {
		return zipFIle;
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
		try (ZipFile d = new ZipFile(zipFIle.toFile())) {
			Path dest = Files.createTempFile(fileLable, ".txt");
			Files.copy(d.getInputStream(d.getEntry(fileName)), dest, StandardCopyOption.REPLACE_EXISTING);
			return dest;
		}
	}

@Override
	public Path getCalendarFile() throws IOException {

		if (calendarFile == null) {

			setCalendarFile(extractFile(CALENDAR_FILE_NAME, "calendar"));
		}

		return calendarFile;

	}

	@Override
	public Path getStopTimeFile() throws IOException {
		if (stopTimeFile == null) {

			setStopTimeFile(extractFile(STOP_TIME_FILE_NAME, "stop_time"));
		}

		return stopTimeFile;
	}
	@Override
	public Path getTripsFile() throws IOException {
		if (tripsFile == null) {

			setTripsFile(extractFile(TRIPS_FILE_NAME, "trips"));
		}

		return tripsFile;
	}
}
