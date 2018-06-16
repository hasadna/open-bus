package il.org.hasadna.siri_client.gtfs.analysis;

import java.io.IOException;
import java.time.LocalDate;
import java.util.Comparator;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.ServiceId;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public class GtfsDataManipulations {

	private GtfsCrud gtfsCrud;

	Stream<Calendar> getCalendarCrud() throws IOException {
		return gtfsCrud.getCalendars();
	}

	Stream<Trip> getTripCrud() throws IOException {
		return gtfsCrud.getTrips();
	}

	Stream<StopTime> getStopTimesCrud() throws IOException {
		return gtfsCrud.getStopTimes();
	}

	public GtfsDataManipulations(GtfsCrud gtfsCrud) {

		this.gtfsCrud = Objects.requireNonNull(gtfsCrud);
	}

	Stream<StopTime> getRelevantStopTimeItems(LocalDate currentDate) throws IOException {

		Set<ServiceId> serviceIds = getRelevantCalendarItems(currentDate).map(Calendar::getServiceId)
				.collect(Collectors.toSet());

		Set<String> tripIds = getTripCrud().filter(i -> serviceIds.contains(i.getServiceId()))
				.map(Trip::getTripId)
				.collect(Collectors.toSet());
		return getUniqueStopTimeItems().filter(i -> tripIds.contains(i.getTripId()));

	}

	public Stream<Integer> getRelevantStopIds(LocalDate currentDate) throws IOException {
		return getRelevantStopTimeItems(currentDate).map(StopTime::getStopId)
				.distinct();
	}

	Stream<Calendar> getRelevantCalendarItems(LocalDate currentDate) throws IOException {

		return getCalendarCrud().filter(c -> c.getStartDate()
				.compareTo(currentDate) <= 0)
				.filter(c -> c.getEndDate()
						.compareTo(currentDate) >= 0)
				.filter(c -> c.isDayValid(currentDate.getDayOfWeek()));

	}

	Stream<StopTime> getUniqueStopTimeItems() throws IOException {
		return getStopTimesCrud().collect(Collectors.groupingBy(StopTime::getTripId, Collectors
				.collectingAndThen(Collectors.maxBy(Comparator.comparing(StopTime::getStopSequence)), Optional::get)))
				.values()
				.stream();
	}

}
