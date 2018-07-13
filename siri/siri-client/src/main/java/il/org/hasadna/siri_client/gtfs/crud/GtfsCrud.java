package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.util.Objects;
import java.util.stream.Stream;


/**
 * 
 * This class represent the main access point for GTFS files.
 * 
 * @author Aviv Sela
 *
 */
public class GtfsCrud {

	GtfsZipFile gtfsZipFile;
	private Crud<Trip> tripCrud;
	private Crud<Calendar> calendarCrud;
	private Crud<StopTime> stopTimesCrud;
	private Crud<Stop> stopsCrud;
	private Crud<Route> routesCrud;

	Crud<Trip> getTripCrud() {
		return tripCrud;
	}

	Crud<Calendar> getCalendarCrud() {
		return calendarCrud;
	}

	Crud<StopTime> getStopTimesCrud() {
		return stopTimesCrud;
	}

	Crud<Stop> getStopsCrud() {
		return stopsCrud;
	}

	Crud<Route> getRoutesCrud() {
		return routesCrud;
	}

	/**
	 * @param gtfsZipFile
	 * @throws IOException if an I/O error occurs when extracting files
	 */
	public GtfsCrud(GtfsZipFile gtfsZipFile) throws IOException {
		this(new TripCrud(gtfsZipFile.extractTripsFile()), 
				new CalendarCrud(gtfsZipFile.extractCalendarFile()),
				new StopTimesCrud(gtfsZipFile.extractStopTimesFile()), 
				new StopsCrud(gtfsZipFile.extractStopsFile()),
				new RoutesCrud(gtfsZipFile.extractRoutesFile())
		);
	}

	/**
	 * @param tripCrud
	 * @param calendarCrud
	 * @param stopTimesCrud
	 * @param stopsCrud
	 */
	public GtfsCrud(Crud<Trip> tripCrud,  Crud<Calendar> calendarCrud, Crud<StopTime> stopTimesCrud, Crud<Stop> stopsCrud, Crud<Route> routesCrud) {
		this.tripCrud = Objects.requireNonNull(tripCrud,"tripCrud");
		this.calendarCrud = Objects.requireNonNull(calendarCrud,"calendarCrud");
		this.stopTimesCrud = Objects.requireNonNull(stopTimesCrud,"stopTimesCrud");
		this.stopsCrud = Objects.requireNonNull(stopsCrud,"stopsCrud");
		this.routesCrud = Objects.requireNonNull(routesCrud,"routesCrud");
	}

	public Stream<Trip> getTrips() throws IOException {
		return getTripCrud().ReadAll();
	}

	/**
	 * @return Stream of calendars instances
	 * @throws IOException
	 *             if an I/O error occurs while reading the Calendars file
	 */
	public Stream<Calendar> getCalendars() throws IOException {
		return getCalendarCrud().ReadAll();
	}

	/**
	 * @return Stream of stop times instances
	 * @throws IOException
	 *             if an I/O error occurs while reading the StopTimes file
	 */
	public Stream<StopTime> getStopTimes() throws IOException {
		return getStopTimesCrud().ReadAll();
	}

	/**
	 * @return Stream of stops instances
	 * @throws IOException
	 *             if an I/O error occurs while reading the Stops file
	 */
	public Stream<Stop> getStops() throws IOException {
		return getStopsCrud().ReadAll();
	}

	public Stream<Route> getRoutes() throws IOException {
		return getRoutesCrud().ReadAll();
	}
}
