package il.org.hasadna.siri_client.gtfs.data;

import java.nio.file.Path;
import static java.util.Objects.requireNonNull;

public class BasicGtfsFiles implements GtfsFiles {
	Path calendarFile;
	Path stopTimeFile;
	Path tripsFile;

	public BasicGtfsFiles(Path calendarFile, Path stopTimeFile, Path tripsFile) {
		requireNonNull(calendarFile, "Calendar file in null");
		requireNonNull(stopTimeFile, "stopTime file in null");
		requireNonNull(tripsFile, "trips file in null");
		this.calendarFile = calendarFile;
		this.stopTimeFile = stopTimeFile;
		this.tripsFile = tripsFile;
	}

	@Override
	public Path getCalendarFile()  {
		return calendarFile;
	}

	@Override
	public Path getStopTimeFile()  {
		return stopTimeFile;
	}

	@Override
	public Path getTripsFile()  {
		return tripsFile;
	}

}
