package il.org.hasadna.siri_client.gtfs.main;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.Collection;

import il.org.hasadna.siri_client.gtfs.analysis.GtfsDataManipulations;
import il.org.hasadna.siri_client.gtfs.analysis.GtfsRecord;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.GtfsFtp;
import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;

public class DefaultGtfsQueryBasedOnFtp {

	private LocalDate date;
	
	private GtfsCrud gtfsCrud;
	
	public DefaultGtfsQueryBasedOnFtp(LocalDate date) throws IOException {
		 this.date = date;
		 System.out.println("111");
		 Path gtfsZip = new GtfsFtp().downloadGtfsZipFile();
		 System.out.println("222");
		 GtfsZipFile gtfsZipFile = new GtfsZipFile(gtfsZip );
		 System.out.println("333");
		 gtfsCrud = new GtfsCrud(gtfsZipFile);
		 System.out.println("444");
	}

	public Collection<GtfsRecord> exec () throws IOException  {
		
		return new GtfsDataManipulations(gtfsCrud).combine(date);
	};
	
	public static void main(String[] args) throws IOException {
		System.out.println(new DefaultGtfsQueryBasedOnFtp(LocalDate.now()).exec().size());
	}

}
