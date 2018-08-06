package il.org.hasadna.siri_client.gtfs.crud;

import java.util.Arrays;
import java.util.Iterator;

public class BaseStop implements Stop {

	int stopId;
	int stopCode;
	String stopName;
	String stopDesc;
	double stopLat;
	double stopLon;
	int locationType;
	int parentStation;
	int zoneId;

	static Stop Parse(String csvRow) {

		Iterator<String> iter = Arrays.asList(csvRow.split(",", -1)).iterator();

		int stopId = strToInt(iter.next());
		int stopCode = strToInt(iter.next());
		String stopName = iter.next();
		String stopDesc = iter.next();
		double stopLat = Double.valueOf(iter.next());
		double stopLon = Double.valueOf(iter.next());
		int locationType = strToInt(iter.next());
		int parentStation = strToInt(iter.next());
		int zoneId = strToInt(iter.next());
		return new BaseStop(stopId, stopCode, stopName, stopDesc, stopLat, stopLon, locationType, parentStation,
				zoneId);
	}

	private static int strToInt(String str) {
		return str.isEmpty() ? 0 : Integer.valueOf(str);
	}

	public BaseStop(int stopId, int stopCode, String stopName, String stopDesc, double stopLat, double stopLon,
			int locationType, int parentStation, int zoneId) {
		super();
		this.stopId = stopId;
		this.stopCode = stopCode;
		this.stopName = stopName;
		this.stopDesc = stopDesc;
		this.stopLat = stopLat;
		this.stopLon = stopLon;
		this.locationType = locationType;
		this.parentStation = parentStation;
		this.zoneId = zoneId;
	}

	@Override
	public int getStopId() {
		return stopId;
	}

	@Override
	public int getStopCode() {
		return stopCode;
	}

	@Override
	public String getStopName() {
		return stopName;
	}

	@Override
	public String getStopDesc() {
		return stopDesc;
	}

	@Override
	public double getStopLat() {
		return stopLat;
	}

	@Override
	public double getStopLon() {
		return stopLon;
	}

	@Override
	public int getLocationType() {
		return locationType;
	}

	@Override
	public int getParentStation() {
		return parentStation;
	}

	@Override
	public int getZoneId() {
		return zoneId;
	}

	@Override
	public String toString() {
		return "BaseStop [stopId=" + stopId + ", stopCode=" + stopCode + ", stopName=" + stopName + ", stopDesc="
				+ stopDesc + ", stopLat=" + stopLat + ", stopLon=" + stopLon + ", locationType=" + locationType
				+ ", parentStation=" + parentStation + ", zoneId=" + zoneId + "]";
	}


	
	
}
