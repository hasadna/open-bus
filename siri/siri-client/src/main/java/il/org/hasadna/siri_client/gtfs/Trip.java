package il.org.hasadna.siri_client.gtfs;

/**
 * Represent a trip file line
 * 
 * @author Aviv Sela
 *
 */

public interface Trip {

	/**
	 * The route_id field contains an ID that uniquely identifies a route. This
	 * value is referenced from the routes.txt file.
	 * 
	 * @return route id
	 */
	String getRouteId();

	/**
	 * The service_id contains an ID that uniquely identifies a set of dates when
	 * service is available for one or more routes. This value is referenced from
	 * the calendar.txt or calendar_dates.txt file.
	 * 
	 * @return Service Id
	 */
	ServiceId getServiceId();

	/**
	 * The trip_id field contains an ID that identifies a trip. The trip_id is
	 * dataset unique.
	 * 
	 * @return Trip Id
	 */
	String getTripId();

	/**
	 * (Optional) The trip_headsign field contains the text that appears on a sign
	 * that identifies the trip's destination to passengers. Use this field to
	 * distinguish between different patterns of service in the same route. If the
	 * headsign changes during a trip, you can override the trip_headsign by
	 * specifying values for the stop_headsign field in stop_times.txt.
	 * 
	 * @return Trip Head-sign
	 */
	String getTripHeadsign();

	/**
	 * (optional) The direction_id field contains a binary value that indicates the
	 * direction of travel for a trip. Use this field to distinguish between
	 * bi-directional trips with the same route_id. This field is not used in
	 * routing; it provides a way to separate trips by direction when publishing
	 * time tables. You can specify names for each direction with the trip_headsign
	 * field.
	 * 
	 * @return Direction Id
	 */
	int getDirectionId();

	/**
	 * The shape_id field contains an ID that defines a shape for the trip. This
	 * value is referenced from the shapes.txt file. The shapes.txt file allows you
	 * to define how a line should be drawn on the map to represent a trip.
	 * 
	 * @return Shape Id
	 */
	int getShapeId();

}