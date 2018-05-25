package il.org.hasadna.siri_client.gtfs;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;

public class BaseCalendar implements Calendar {

	private String serviceId;
	private EnumSet<Day> validDays;
	private LocalDate startDate;
	private LocalDate endDate;

	static DateTimeFormatter dateFormat = DateTimeFormatter.ofPattern("yyyyMMdd");

	public static BaseCalendar parse(String csvRow) {

		List<String> fields = Arrays.asList(csvRow.split(",", -1));

		if (fields.size() != 10) {
			throw new IllegalArgumentException("Calendar CSV row Should contains 10 fields");
		}
		;

		Iterator<String> fieldsIter = fields.iterator();

		String serviceId = fieldsIter.next();
		EnumSet<Day> validDays = EnumSet.noneOf(Day.class);
		for (Day day : Day.values()) {
			if (fieldsIter.next().equals("1")) {
				validDays.add(day);
			}
		}

		LocalDate startDate = LocalDate.parse(fieldsIter.next(), dateFormat);
		LocalDate endDate = LocalDate.parse(fieldsIter.next(), dateFormat);
		return new BaseCalendar(serviceId, validDays, startDate, endDate);
	}

	BaseCalendar(String serviceId, EnumSet<Day> validDays, LocalDate startDate, LocalDate endDate) {
		this.serviceId = serviceId;
		this.validDays = validDays;
		this.startDate = startDate;
		this.endDate = endDate;
	}

	@Override
	public String getServiceId() {
		return serviceId;
	}

	@Override
	public EnumSet<Day> getValidDays() {
		return validDays;
	}

	@Override
	public boolean isValid(Day day) {
		return validDays.contains(day);
	}

	@Override
	public LocalDate getStartDate() {
		return startDate;
	}

	@Override
	public LocalDate getEndDate() {
		return endDate;
	}

}
