package il.org.hasadna.siri_client.gtfs.main;

import static org.junit.Assert.*;

import java.io.IOException;
import java.time.LocalDate;
import java.util.Collection;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.analysis.GtfsRecord;

public class DefaultGtfsQueryBasedOnFtpTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	
	public void testExec() throws IOException {
		DefaultGtfsQueryBasedOnFtp defaultGtfsQueryBasedOnFtp = new DefaultGtfsQueryBasedOnFtp(LocalDate.now());
		Collection<GtfsRecord> res = defaultGtfsQueryBasedOnFtp.exec();
		
		res.forEach(System.out::println);
	}

}
