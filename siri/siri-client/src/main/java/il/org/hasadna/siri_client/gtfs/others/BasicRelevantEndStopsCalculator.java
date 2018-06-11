package il.org.hasadna.siri_client.gtfs.others;

import java.io.IOException;
import java.time.LocalDate;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import il.org.hasadna.siri_client.gtfs.Calendar;
import il.org.hasadna.siri_client.gtfs.ServiceId;
import il.org.hasadna.siri_client.gtfs.StopTime;
import il.org.hasadna.siri_client.gtfs.Trip;

public class BasicRelevantEndStopsCalculator implements RelevantEndStopsCalculator {

	private static final LocalDate CURRENT_DATE = null;

	protected Stream<Calendar> getRelevantCalendarItems(LocalDate currentDate) {
		return null;

	}

	protected Stream<Trip> getRelevantTripsItems() {
		return null;
	}

	protected Stream<StopTime> getRelevantStopTimeItems() {
		return null;

	}

	@Override
	public Stream<Stop> getStreamOfRelevantEndStops() {

		Set<ServiceId> serviceIds = getRelevantCalendarItems(CURRENT_DATE).map(Calendar::getServiceId)
				.collect(Collectors.toSet());

		Set<String> tripIds = getRelevantTripsItems().filter(i -> serviceIds.contains(i.getServiceId()))
				.map(Trip::getTripId).collect(Collectors.toSet());
		return getRelevantStopTimeItems().filter(i -> tripIds.contains(i.getTripId())).map(i -> i.getStopId())
				.distinct().map(BasicStop::new);
	}

}
