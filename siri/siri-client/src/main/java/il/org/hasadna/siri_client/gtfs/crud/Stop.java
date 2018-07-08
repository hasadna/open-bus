package il.org.hasadna.siri_client.gtfs.crud;

public interface Stop {

	/**
	 * The stop_id field contains an ID that uniquely identifies a stop, station, or
	 * station entrance. Multiple routes may use the same stop. The stop_id is used
	 * by systems as an internal identifier of this record (e.g., primary key in
	 * database), and therefore the stop_id must be dataset unique.
	 * 
	 * @return Stop ID
	 */
	int getStopId();

	/**
	 * The stop_code field contains short text or a number that uniquely identifies
	 * the stop for passengers. Stop codes are often used in phone-based transit
	 * information systems or printed on stop signage to make it easier for riders
	 * to get a stop schedule or real-time arrival information for a particular
	 * stop. The stop_code field contains short text or a number that uniquely
	 * identifies the stop for passengers. The stop_code can be the same as stop_id
	 * if it is passenger-facing. This field should be left blank for stops without
	 * a code presented to passengers.
	 * 
	 * @return Stop Code
	 */
	int getStopCode();

	/**
	 * The stop_name field contains the name of a stop, station, or station
	 * entrance. Please use a name that people will understand in the local and
	 * tourist vernacular.
	 * 
	 * @return Stop Name
	 */
	String getStopName();

	/**
	 * The stop_desc field contains a description of a stop. Please provide useful,
	 * quality information. Do not simply duplicate the name of the stop.
	 * 
	 * @return Stop Description
	 */
	String getStopDesc();

	/**
	 * The stop_lat field contains the latitude of a stop, station, or station
	 * entrance. The field value must be a valid WGS 84 latitude.
	 * 
	 * @return Stop Latitude
	 */
	double getStopLat();

	/**
	 * The stop_lon field contains the longitude of a stop, station, or station
	 * entrance. The field value must be a valid WGS 84 longitude value from -180 to
	 * 180.
	 * 
	 * @return Stop Longitude
	 */
	double getStopLon();

	/**
	 * The location_type field identifies whether this stop ID represents a stop,
	 * station, or station entrance. If no location type is specified, or the
	 * location_type is blank, stop IDs are treated as stops. Stations may have
	 * different properties from stops when they are represented on a map or used in
	 * trip planning. The location type field can have the following values:
	 * 
	 * @return Location Type
	 */
	int getLocationType();

	/**
	 * For stops that are physically located inside stations, the parent_station
	 * field identifies the station associated with the stop. To use this field,
	 * stops.txt must also contain a row where this stop ID is assigned location
	 * type=1.
	 * 
	 * @return Parent Station
	 */
	int getParentStation();

	/**
	 * The zone_id field defines the fare zone for a stop ID. Zone IDs are required
	 * if you want to provide fare information using fare_rules.txt. If this stop ID
	 * represents a station, the zone ID is ignored.
	 * 
	 * @return Zone ID
	 */
	int getZoneId();

}