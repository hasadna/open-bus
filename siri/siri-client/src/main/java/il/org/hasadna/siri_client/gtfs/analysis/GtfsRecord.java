package il.org.hasadna.siri_client.gtfs.analysis;

import il.org.hasadna.siri_client.gtfs.crud.Calendar;
import il.org.hasadna.siri_client.gtfs.crud.Stop;
import il.org.hasadna.siri_client.gtfs.crud.StopTime;
import il.org.hasadna.siri_client.gtfs.crud.Trip;

public class GtfsRecord {

	Trip trip;
	Calendar calendar; 
	StopTime firstStopTime;
	Stop firstStop;
	StopTime lastStopTime;
	Stop lastStop;
	
	
	GtfsRecord(Trip trip, Calendar calendar, StopTime firstStopTime, Stop firstStop, StopTime lastStopTime,
			Stop lastStop) {
		
		this.trip = trip;
		this.calendar = calendar;
		this.firstStopTime = firstStopTime;
		this.firstStop = firstStop;
		this.lastStopTime = lastStopTime;
		this.lastStop = lastStop;
	}
	
	
	


}
