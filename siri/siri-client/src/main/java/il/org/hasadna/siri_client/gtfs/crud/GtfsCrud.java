package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.util.stream.Stream;

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
		tripCrud = new TripCrud(gtfsZipFile.getTripsFile());
		calendarCrud = new CalendarCrud(gtfsZipFile.getCalendarFile());
		stopTimesCrud = new StopTimesCrud(gtfsZipFile.getStopTimesFile());
	}

	public Stream<Trip> getTrips() throws IOException {
		return getTripCrud().ReadAll();
	}

	public Stream<Calendar> getCalendars() throws IOException {
		return getCalendarCrud().ReadAll();
	}

	public Stream<StopTime> getStopTimes() throws IOException {
		return getStopTimesCrud().ReadAll();
	}

}
