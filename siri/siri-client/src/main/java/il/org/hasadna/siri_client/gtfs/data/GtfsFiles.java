package il.org.hasadna.siri_client.gtfs.data;

import java.io.IOException;
import java.nio.file.Path;

public interface GtfsFiles {

	Path getCalendarFile() throws IOException;

	Path getStopTimeFile() throws IOException;

	Path getTripsFile() throws IOException;

}
