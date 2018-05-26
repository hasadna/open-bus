package il.org.hasadna.siri_client.gtfs;

import java.io.IOException;
import java.nio.file.Path;

/**
 * @author Aviv Sela
 *
 */
public class TripCrud extends AbstractFileCrud<Trip> {

	public TripCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	Trip parseLine(String string) {
		return BaseTrip.parse(string);
	}

}
