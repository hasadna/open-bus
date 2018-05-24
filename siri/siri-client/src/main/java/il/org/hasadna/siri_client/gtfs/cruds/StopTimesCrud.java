package il.org.hasadna.siri_client.gtfs.cruds;

import java.io.IOException;
import java.nio.file.Path;

import il.org.hasadna.siri_client.gtfs.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.StopTime;



public class StopTimesCrud extends AbstractFileCrud<StopTime> {

	public StopTimesCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	StopTime parseLine(String string) {
		return BaseStopTime.parse(string);
	}

}
