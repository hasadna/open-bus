package il.org.hasadna.siri_client.gtfs.cruds;

import java.io.IOException;
import java.nio.file.Path;

import il.org.hasadna.siri_client.gtfs.BaseTrip;
import il.org.hasadna.siri_client.gtfs.Trip;


public class TripCrud extends AbstractFileCrud<Trip> {

	public TripCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	Trip parseLine(String string) {
		return BaseTrip.parse(string);
	}

}
