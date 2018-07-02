package il.org.hasadna.siri_client.gtfs.analysis;

import java.time.LocalDate;
import java.util.Collection;

public interface GtfsResult {

	String getDescription();
	int getStopCode();
	int get‫‪RouteID‬‬();
	Collection<LocalDate> getDepartureTimesFromFirstStop();
}
