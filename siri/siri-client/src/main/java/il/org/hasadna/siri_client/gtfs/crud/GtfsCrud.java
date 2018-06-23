package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.util.stream.Stream;

/**
 * 
 * This class represent the main access point for GTFS files.
 * @author Aviv Sela
 *
 */
public class GtfsCrud {

	GtfsZipFile gtfsZipFile;
	private TripCrud tripCrud;
	private CalendarCrud calendarCrud;
	private StopTimesCrud stopTimesCrud;

	TripCrud getTripCrud() {
		return tripCrud;
	}

	CalendarCrud getCalendarCrud() {
		return calendarCrud;
	}

	StopTimesCrud getStopTimesCrud() {
		return stopTimesCrud;
	}

	public GtfsCrud(GtfsZipFile gtfsZipFile) throws IOException {
		tripCrud = new TripCrud(gtfsZipFile.extractTripsFile());
		calendarCrud = new CalendarCrud(gtfsZipFile.extractCalendarFile());
		stopTimesCrud = new StopTimesCrud(gtfsZipFile.extractStopTimesFile());
	}

	/**
	 * @return Stream of trips instances
	 * @throws IOException
	 */
	public Stream<Trip> getTrips() throws IOException {
		return getTripCrud().ReadAll();
	}
	/**
	 * @return Stream of calendars instances
	 * @throws IOException
	 */
	public Stream<Calendar> getCalendars() throws IOException {
		return getCalendarCrud().ReadAll();
	}
	/**
	 * @return Stream of stop times instances
	 * @throws IOException
	 */
	public Stream<StopTime> getStopTimes() throws IOException {
		return getStopTimesCrud().ReadAll();
	}

}
