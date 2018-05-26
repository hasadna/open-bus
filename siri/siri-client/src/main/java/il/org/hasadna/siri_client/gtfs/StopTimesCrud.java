package il.org.hasadna.siri_client.gtfs;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * @author Aviv Sela
 *
 */
public class StopTimesCrud extends AbstractFileCrud<StopTime> {

	public StopTimesCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	StopTime parseLine(String string) {
		return BaseStopTime.parse(string);
	}

	public Stream<StopTime> getRelevantStopTimeItems() throws IOException {
		return ReadAll()
				.collect(Collectors.groupingBy(StopTime::getTripId, Collectors.collectingAndThen(
						Collectors.maxBy(Comparator.comparing(StopTime::getStopSequence)), Optional::get)))
				.values().stream();
	}

}
