package il.org.hasadna.siri_client.gtfs;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.StopTime;
import il.org.hasadna.siri_client.gtfs.StopTimesCrud;

public class StopTimesCrudTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testReadAll() throws IOException {

		StopTimesCrud stopTimesCrud = new StopTimesCrud(
				Paths.get("src/test/resources/siri_client/gtfs/cruds/min_stop_times.txt"));
		List<StopTime> actual = stopTimesCrud.ReadAll().collect(Collectors.toList());

		List<StopTime> expected = Arrays.asList(BaseStopTime.parse("32217742_200518,22:20:00,22:20:00,37358,1,0,1,0"),
				BaseStopTime.parse("32217742_200518,22:22:00,22:22:00,37350,2,0,0,1400"),
				BaseStopTime.parse("32217742_200518,22:27:00,22:27:00,37292,3,0,0,3700"));

		assertEquals(expected, actual);

	}

	@Test
	public void testStopTimesCrud() throws IOException {
		new StopTimesCrud(Paths.get("src/test/resources/siri_client/gtfs/cruds/min_stop_times.txt"));
	}

	@Test(expected = IOException.class)
	public void testStopTimesCrud_non_exist() throws IOException {
		Path path = Paths.get("non/exist/file.txt");
		new StopTimesCrud(path);
	}

	@Test

	public void testgetRelevantStopTimeItems() throws IOException {
		// Prepare
		String tripIdA = "tripIdA";
		String tripIdB = "tripIdB";
		String arrivalTime = "";
		String departureTime = "";
		int stopId = 0;
		int pickupType = 0;
		int dropOffType = 0;
		int shapeDistTraveled = 0;

		StopTime stopTime1 = new BaseStopTime(tripIdB, arrivalTime, departureTime, stopId, 1, pickupType, dropOffType,
				shapeDistTraveled);
		StopTime stopTime2 = new BaseStopTime(tripIdA, arrivalTime, departureTime, stopId, 2, pickupType, dropOffType,
				shapeDistTraveled);
		StopTime stopTime3 = new BaseStopTime(tripIdA, arrivalTime, departureTime, stopId, 3, pickupType, dropOffType,
				shapeDistTraveled);

		StopTimesCrud stopTimesCrudStub = new StopTimesCrud(
				Paths.get("src/test/resources/siri_client/gtfs/cruds/min_stop_times.txt")) {
			@Override
			public Stream<StopTime> ReadAll() throws IOException {

				return Arrays.asList(stopTime1, stopTime2, stopTime3).stream();
			}

		};

		// Expected - get last stop time of trip A and last stop time of trip B
		Set<StopTime> expected = new HashSet<>(Arrays.asList(stopTime1, stopTime3));
		// Execute
		Set<StopTime> actual = stopTimesCrudStub.getRelevantStopTimeItems().collect(Collectors.toSet());
		// Test
		assertEquals(expected, actual);

	}

}
