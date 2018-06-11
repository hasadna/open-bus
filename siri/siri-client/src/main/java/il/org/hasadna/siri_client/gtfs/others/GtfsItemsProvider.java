package il.org.hasadna.siri_client.gtfs.others;

import java.util.stream.Stream;

public interface GtfsItemsProvider {
	Stream<CalendarItem> getStreamOfCalendarsItems();
	Stream<TripItem> getStreamOfTripsItems();
	Stream<StopTimeItem> StreamOfStopTimeItems();
}
