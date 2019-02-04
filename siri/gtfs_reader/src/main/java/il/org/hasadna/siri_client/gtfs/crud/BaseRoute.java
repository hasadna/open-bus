package il.org.hasadna.siri_client.gtfs.crud;

import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

/**
 * @author Evyatar Kafkafi
 *
 */
public class BaseRoute implements Route {

	private String routeId;
	private String agencyId;
	private String routeShortName;
	private String routeLongName;
	private String routeDesc;

	public static BaseRoute parse(String csvRow) {

		List<String> fields = Arrays.asList(csvRow.split(",", -1));

		if (fields.size() < 5) {
			throw new IllegalArgumentException("Route CSV row Should contains at least 5 fields");
		}

		Iterator<String> fieldsIter = fields.iterator();

		String routeId = new String(fieldsIter.next());
		String agencyId = new String(fieldsIter.next());
		String routeShortName = new String(fieldsIter.next());
		String routeLongName = new String(fieldsIter.next());
		String routeDesc = new String(fieldsIter.next());

		return new BaseRoute(routeId, agencyId, routeShortName, routeLongName, routeDesc);
	}

	public BaseRoute(String rRouteId, String agencyId, String routeShortName, String routeLongName, String routeDesc) {
		this.routeId = rRouteId;
		this.agencyId = agencyId;
		this.routeShortName = routeShortName;
		this.routeLongName = routeLongName;
		this.routeDesc = routeDesc;
	}

	@Override
	public String toString() {
		return "BaseRoute{" +
				"routeId='" + routeId + '\'' +
				", agencyId='" + agencyId + '\'' +
				", routeShortName='" + routeShortName + '\'' +
				", routeLongName='" + routeLongName + '\'' +
				", routeDesc='" + routeDesc + '\'' +
				'}';
	}


	@Override
	public String getRouteId() {
		return routeId;
	}

	@Override
	public String getAgencyId() {
		return agencyId;
	}

	@Override
	public String getRouteShortName() {
		return routeShortName;
	}

	@Override
	public String getRouteLongName() {
		return routeLongName;
	}

	@Override
	public String getRouteDesc() {
		return routeDesc;
	}
}
