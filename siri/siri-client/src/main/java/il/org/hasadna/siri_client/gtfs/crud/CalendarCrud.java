package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.stream.Stream;

/**
 * @author Aviv Sela
 *
 */
public class CalendarCrud extends AbstractFileCrud<Calendar> {

	public CalendarCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	Calendar parseLine(String string) {
		return BaseCalendar.parse(string);
	}

	public Stream<Calendar> getRelevantCalendarItems(LocalDate currentDate) throws IOException {

		return ReadAll().filter(c -> c.getStartDate()
				.compareTo(currentDate) < 0)
				.filter(c -> c.getEndDate()
						.compareTo(currentDate) > 0)
				.filter(c -> c.isDayValid(currentDate.getDayOfWeek()));
	}

}
