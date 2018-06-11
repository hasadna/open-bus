package il.org.hasadna.siri_client.gtfs.others;

import static org.junit.Assert.*;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.EnumSet;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.BaseStopTime;
import il.org.hasadna.siri_client.gtfs.BaseTrip;
import il.org.hasadna.siri_client.gtfs.Calendar;
import il.org.hasadna.siri_client.gtfs.ServiceId;
import il.org.hasadna.siri_client.gtfs.StopTime;
import il.org.hasadna.siri_client.gtfs.Trip;

public class RelevantEndStopsCalculatorTest {

	@Before
	public void setUp() throws Exception {
	}

	@Test
	public void testGetStreamOfRelevantEndStops() {
		RelevantEndStopsCalculator relevantEndStopsCalculator = new BasicRelevantEndStopsCalculator() {
			@Override
			protected Stream<Calendar> getRelevantCalendarItems(LocalDate currentDate) {
				return Stream.of(new BaseCalendar(new ServiceId("100"), EnumSet.noneOf(DayOfWeek.class), LocalDate.MIN,
						LocalDate.MAX));
			}

			@Override
			protected Stream<StopTime> getRelevantStopTimeItems() {
				return Stream.of(new BaseStopTime("200", "", "", 314, 5, 0, 0, 0));
			}

			@Override
			protected Stream<Trip> getRelevantTripsItems() {
				return Stream.of(new BaseTrip("", new ServiceId("100"), "200", "", 0, 0));
			}

		};

		assertTrue(relevantEndStopsCalculator.getStreamOfRelevantEndStops() != null);
	}

}
