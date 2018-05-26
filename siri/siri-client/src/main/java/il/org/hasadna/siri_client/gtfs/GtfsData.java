package il.org.hasadna.siri_client.gtfs;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class GtfsData {

	private CalendarCrud calendarCrud;
	private TripCrud tripCrud;
	private StopTimesCrud stopTimesCrud;

	public GtfsData(Path calendarCrud, Path tripCrud, Path stopTimesCrud) throws IOException {
		this(new CalendarCrud(calendarCrud), new TripCrud(tripCrud), new StopTimesCrud(stopTimesCrud));
	}

	public GtfsData(CalendarCrud calendarCrud, TripCrud tripCrud, StopTimesCrud stopTimesCrud) {

		this.calendarCrud = calendarCrud;
		this.tripCrud = tripCrud;
		this.stopTimesCrud = stopTimesCrud;
	}

	public Stream<StopTime> getRelevantStopTimeItems(LocalDate currentDate) throws IOException {

		Set<ServiceId> serviceIds = calendarCrud.getRelevantCalendarItems(currentDate).map(Calendar::getServiceId)
				.collect(Collectors.toSet());

		Set<String> tripIds = tripCrud.ReadAll().filter(i -> serviceIds.contains(i.getServiceId())).map(Trip::getTripId)
				.collect(Collectors.toSet());
		return stopTimesCrud.getRelevantStopTimeItems().filter(i -> tripIds.contains(i.getTripId()));

	}

	public Stream<Integer> getRelevantStopIds(LocalDate currentDate) throws IOException {
		return getRelevantStopTimeItems(currentDate).map(StopTime::getStopId).distinct();
	}

}
