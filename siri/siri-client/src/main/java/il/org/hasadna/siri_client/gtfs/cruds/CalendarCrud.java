package il.org.hasadna.siri_client.gtfs.cruds;

import java.io.IOException;
import java.nio.file.Path;

import il.org.hasadna.siri_client.gtfs.BaseCalendar;
import il.org.hasadna.siri_client.gtfs.Calendar;

public class CalendarCrud extends AbstractFileCrud<Calendar> {

	public CalendarCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	Calendar parseLine(String string) {
		return BaseCalendar.parse(string);
	}

}
