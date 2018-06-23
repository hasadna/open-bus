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

	Stream<Calendar> getCalendarItems() throws IOException {
		return gtfsCrud.getCalendars();
	}

	Stream<Trip> getTripItems() throws IOException {
		return gtfsCrud.getTrips();
	}

	Stream<StopTime> getStopTimesItems() throws IOException {
		return gtfsCrud.getStopTimes();
	}

	public GtfsDataManipulations(GtfsCrud gtfsCrud) {

		this.gtfsCrud = Objects.requireNonNull(gtfsCrud);
	}

	Stream<StopTime> getRelevantStopTimeItems(LocalDate currentDate) throws IOException {

		Set<ServiceId> serviceIds = getRelevantCalendarItems(currentDate).map(Calendar::getServiceId)
				.collect(Collectors.toSet());

		Set<String> tripIds = getTripItems().filter(i -> serviceIds.contains(i.getServiceId()))
				.map(Trip::getTripId)
				.collect(Collectors.toSet());
		return getLastStopTimeItems().filter(i -> tripIds.contains(i.getTripId()));

	}

	public Stream<Integer> getRelevantStopIds(LocalDate currentDate) throws IOException {
		return getRelevantStopTimeItems(currentDate).map(StopTime::getStopId)
				.distinct();
	}

	Stream<Calendar> getRelevantCalendarItems(LocalDate currentDate) throws IOException {

		return getCalendarItems().filter(c -> c.getStartDate()
				.compareTo(currentDate) <= 0)
				.filter(c -> c.getEndDate()
						.compareTo(currentDate) >= 0)
				.filter(c -> c.isDayValid(currentDate.getDayOfWeek()));

	}

	/**
	 * 
	 * the method is used to get for each trip the stop time of the last station
	 * @return StopTimes represent the stop time of the last station
	 * @throws IOException
	 */
	Stream<StopTime> getLastStopTimeItems() throws IOException {
		return getStopTimesItems().collect(Collectors.groupingBy(StopTime::getTripId, Collectors
				.collectingAndThen(Collectors.maxBy(Comparator.comparing(StopTime::getStopSequence)), Optional::get)))
				.values()
				.stream();
	}

}
