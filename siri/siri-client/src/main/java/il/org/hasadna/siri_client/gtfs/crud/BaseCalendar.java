package il.org.hasadna.siri_client.gtfs.crud;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;

/**
 * @author Aviv Sela
 *
 */
public class BaseCalendar implements Calendar {

	private ServiceId serviceId;
	private EnumSet<DayOfWeek> validDays;
	private LocalDate startDate;
	private LocalDate endDate;

	static DateTimeFormatter dateFormat = DateTimeFormatter.ofPattern("yyyyMMdd");

	public static BaseCalendar parse(String csvRow) {

		List<String> fields = Arrays.asList(csvRow.split(",", -1));

		if (fields.size() != 10) {
			throw new IllegalArgumentException("Calendar CSV row Should contains 10 fields");
		}

		Iterator<String> fieldsIter = fields.iterator();

		ServiceId serviceId = new ServiceId(fieldsIter.next());
		EnumSet<DayOfWeek> validDays = EnumSet.noneOf(DayOfWeek.class);
		for (DayOfWeek day : Arrays.asList(DayOfWeek.SUNDAY, DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY,
				DayOfWeek.THURSDAY, DayOfWeek.FRIDAY, DayOfWeek.SATURDAY)) {
			if (fieldsIter.next()
					.equals("1")) {
				validDays.add(day);
			}
		}

		LocalDate startDate = LocalDate.parse(fieldsIter.next(), dateFormat);
		LocalDate endDate = LocalDate.parse(fieldsIter.next(), dateFormat);
		return new BaseCalendar(serviceId, validDays, startDate, endDate);
	}

	public BaseCalendar(ServiceId serviceId, EnumSet<DayOfWeek> validDays, LocalDate startDate, LocalDate endDate) {
		this.serviceId = serviceId;
		this.validDays = validDays;
		this.startDate = startDate;
		this.endDate = endDate;
	}

	@Override
	public ServiceId getServiceId() {
		return serviceId;
	}

	@Override
	public EnumSet<DayOfWeek> getValidDays() {
		return validDays;
	}

	@Override
	public boolean isDayValid(DayOfWeek day) {
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
