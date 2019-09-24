package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.nio.file.Path;

/**
 * @author Evyatar
 *
 */
public class RoutesCrud extends AbstractFileCrud<Route> {

	public RoutesCrud(Path file) throws IOException {
		super(file);
	}

	@Override
	Route parseLine(String string) {
		return BaseRoute.parse(string);
	}


}
