package il.org.hasadna.siri_client.gtfs.others;

import java.nio.file.Path;

public interface GtfsFilesProvider {
	Path getCalendarFile();
	Path getTripsFile();
	Path getStopTImeFile();
}
