package il.org.hasadna.siri_client.gtfs;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDate;

import il.org.hasadna.siri_client.gtfs.data.GtfsWorkspace;

public class Main {

	public static void main(String[] args) throws IOException {
		LocalDate currentDate = LocalDate.now();
		Path ftpDestFolder = executeFtpDownloadApp();
		GtfsWorkspace gtfsWorkspace = new GtfsWorkspace(ftpDestFolder);
		GtfsDataManipulations gtfsDataManipulations = new GtfsDataManipulations(gtfsWorkspace.getCalendarFile(), gtfsWorkspace.getTripsFile(), gtfsWorkspace.getStopTimeFile());
		
		gtfsDataManipulations.getRelevantStopIds(currentDate);
	}

	private static Path executeFtpDownloadApp() throws IOException {
		
		Runtime.getRuntime().exec("python3 gtfs_retrieve.py -d .", null, null);
		
return null;
	}

}
