package il.org.hasadna.siri_client.gtfs.cruds;

import static org.junit.Assert.*;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.StopTime;



public class StopTimesCrudTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testReadAll() throws IOException {

		StopTimesCrud stopTimesCrud = new StopTimesCrud(Paths.get("src/test/resources/siri_client/gtfs/cruds/min_stop_times.txt"));
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
		new StopTimesCrud(Paths.get("non/exist/file.txt"));
	}
	
}
