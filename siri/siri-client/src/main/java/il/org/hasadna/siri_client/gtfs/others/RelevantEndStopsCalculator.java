package il.org.hasadna.siri_client.gtfs.others;

import java.util.stream.Stream;

public interface RelevantEndStopsCalculator {
	Stream<Stop> getStreamOfRelevantEndStops();
}
