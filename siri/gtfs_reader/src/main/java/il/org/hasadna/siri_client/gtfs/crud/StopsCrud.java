package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.nio.file.Path;

public class StopsCrud extends AbstractFileCrud<Stop> {

	public StopsCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	Stop parseLine(String string) {
		return BaseStop.Parse(string);
	}

}
