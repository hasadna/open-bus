package il.org.hasadna.siri_client.gtfs.data;

import java.nio.file.Path;

public enum GtfsFiles {
	CALENDAR, TRIP, STOP_TIME;
	
	private Path path;

	Object lock = new Object();
	
	Path getPath() {
		synchronized (lock) {
			return path;
		}
	}

	void setPath(Path path) {
		synchronized (lock) {	
			this.path = path;
			
		}
	}
}
